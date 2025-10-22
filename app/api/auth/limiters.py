import json
from fastapi import Response
from datetime import datetime, timezone

from app.config import settings
from app.services.redis import RedisService

from app.utils.datetime import utc_now
from app.utils.common import generate_uuid
from app.exceptions.common import TooManyRequestsException
from app.limiters.abstract import AbstractLimiter


class VerificationLimiter(AbstractLimiter):
    def __init__(
        self,
        max_attempts: int = settings.VERIFICATION.MAX_ATTEMPTS,
        block_time: int = settings.VERIFICATION.BAN_TIME_SECONDS,
        cookie_ttl: int = settings.VERIFICATION.BAN_TIME_SECONDS,
    ):
        super().__init__()
        self.max_attempts = max_attempts
        self.block_time = block_time
        self.cookie_ttl = cookie_ttl
        self.cache = RedisService(
            dsn=settings.REDIS.REDIS_URL,
            prefix="auth"
        )

    @staticmethod
    def _get_or_create_session_id(cookie_value: str | None) -> tuple[str, bool]:
        session_id = cookie_value
        is_new = False

        if not session_id:
            session_id = generate_uuid()
            is_new = True

        return session_id, is_new

    @staticmethod
    def _get_cache_key(session_id: str) -> str:
        return f"{settings.VERIFICATION.COOKIE_NAME}:verification_{session_id}"

    async def _get_data(self, key: str) -> dict:
        data = await self.cache.get_value(key)
        if data:
            return json.loads(data)
        return {"attempts": 0, "blocked_until": None}

    async def _set_data(self, key: str, data: dict) -> None:
        await self.cache.set_value(key=key, value=json.dumps(data), ttl=self.block_time)

    async def check_and_prepare(self, session_id: str | None) -> tuple[str, bool]:
        session_id, is_new = self._get_or_create_session_id(cookie_value=session_id)

        key = self._get_cache_key(session_id)
        data = await self._get_data(key)

        current_time = utc_now()
        if data.get("blocked_until"):

            blocked_until = data["blocked_until"]

            if isinstance(blocked_until, (int, float)):
                blocked_until = datetime.fromtimestamp(blocked_until, tz=timezone.utc)

            if current_time < blocked_until:
                remaining = int((blocked_until - current_time).total_seconds())
                raise TooManyRequestsException(
                    message=f"Too many failed attempts. Retry in {remaining} seconds.",
                    headers={"Retry-After": str(remaining)},
                )

        return session_id, is_new

    async def record_failure(self, session_id: str) -> None:
        key = self._get_cache_key(session_id)
        data = await self._get_data(key)

        data["attempts"] += 1

        if data["attempts"] >= self.max_attempts:
            data["blocked_until"] = utc_now().timestamp() + self.block_time

        await self._set_data(key, data)

    async def reset(self, session_id: str | None) -> None:
        if session_id:
            key = self._get_cache_key(session_id=session_id)
            await self.cache.delete(key)

    def _set_session_cookie(self, response: Response, session_id: str):
        response.set_cookie(
            key=settings.VERIFICATION.COOKIE_NAME,
            value=session_id,
            max_age=self.cookie_ttl,
            httponly=True,
            secure=True,
            samesite="lax",
        )
