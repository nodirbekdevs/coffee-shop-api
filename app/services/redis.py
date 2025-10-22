from redis.asyncio import Redis


class RedisService:
    def __init__(
        self,
        dsn: str,
        prefix: str = "app",
        encoding: str = "utf-8",
        decode_responses: bool = True,
    ):
        self.redis = Redis.from_url(
            dsn, encoding=encoding, decode_responses=decode_responses
        )
        self.prefix = prefix

    def _key(self, name: str) -> str:
        return f"{self.prefix}:{name}"

    async def set_value(self, key: str, value: str, ttl: int | None = None):
        full_key = self._key(key)
        if ttl:
            await self.redis.set(full_key, value, ex=ttl)
        else:
            await self.redis.set(full_key, value)

    async def get_value(self, key: str) -> str | None:
        return await self.redis.get(self._key(key))

    async def increment(self, key: str, ttl: int | None = None) -> int:
        full_key = self._key(key)
        attempts = await self.redis.incr(full_key)
        if attempts == 1 and ttl:
            await self.redis.expire(full_key, ttl)
        return attempts

    async def delete(self, key: str):
        await self.redis.delete(self._key(key))
