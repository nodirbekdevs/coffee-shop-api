import datetime

from app.config import settings
from app.exceptions.verification import SmsCodeTimeoutException
from app.utils.datetime import utc_now
from app.fields.common import ModelOrderByRule
from app.utils.common import hash_security_code
from app.models.verification import Verification
from app.repositories.base import BaseRepository
from app.exceptions.common import ObjectNotFoundException, InvalidDataException


class VerificationRepository(BaseRepository):
    model = Verification

    @staticmethod
    def _check_security_code_expiry(token_created_time: datetime) -> None:
        time_difference = utc_now() - token_created_time
        return time_difference.seconds > settings.VERIFICATION.EXPIRE_SECONDS

    async def check_limit(
            self,
            contact: str,
            retry_limit: int = settings.VERIFICATION.RETRY_LIMIT,
            timeout_seconds: int = settings.VERIFICATION.TIMEOUT_SECONDS,
            ban_time_seconds: int = settings.VERIFICATION.BAN_TIME_SECONDS,
    ):
        last_verifications = await self.find_all(
            orderings=[ModelOrderByRule(field="created_at", desc=True)], contact=contact
        )

        if len(last_verifications) == retry_limit:
            objs_time_difference = (
                    last_verifications[0].created_at
                    - last_verifications[retry_limit - 1].created_at
            )
            now = utc_now()
            time_difference = now - last_verifications[0].created_at

            if (
                    objs_time_difference.total_seconds() <= timeout_seconds
                    and time_difference.total_seconds() <= ban_time_seconds
            ):
                raise SmsCodeTimeoutException()

    @staticmethod
    def _check_token_expiry(token_created_time: datetime) -> bool:
        time_difference = utc_now() - token_created_time
        return time_difference.seconds > settings.VERIFICATION.TOKEN_EXPIRY_SECONDS

    async def check_token(self, contact: str, token: str, action: str) -> None:
        verification = await self.find_one_or_none(
            contact=contact, token=token, action=action
        )
        if not verification:
            raise ObjectNotFoundException(
                message="The verification code token not found",
                message_key="verification_code_token_not_found",
            )
        if self._check_token_expiry(token_created_time=verification.created_at):
            raise InvalidDataException(
                message="The verification token has expired",
                message_key="verification_token_expired",
            )
        if not verification.is_verified:
            raise InvalidDataException(
                message="The verification token not verified",
                message_key="verification_token_not_verified",
            )
        return

    @staticmethod
    def _hash_security_code(security_code: str) -> str:
        return hash_security_code(security_code)

    async def code_verify(self, security_code: str, user_id: int):
        hashed_security_code = self._hash_security_code(security_code=security_code)
        verification = await self.find_one_or_none(
            user_id=user_id, security_code=hashed_security_code
        )

        if not verification:
            raise ObjectNotFoundException(
                message="The verification code is invalid",
                message_key="verification_code_invalid",
            )
        if self._check_security_code_expiry(verification.created_at):
            raise InvalidDataException(
                message="The verification code has expired",
                message_key="verification_code_expired",
            )
        if verification.is_verified:
            raise InvalidDataException(
                message="The verification code is already verified",
                message_key="verification_code_already_verified",
            )
        return verification

