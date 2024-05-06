from typing import Any, Optional, Set, Union

from redis.asyncio import ConnectionPool, Redis

from .base import BaseMailerStorage, StorageRecord


DEFAULT_KEY_PREFIX = "mailer"
DEFAULT_KEY_SEPERATOR = ":"


class RedisMailerStorage(BaseMailerStorage):
    redis: Redis
    key_prefix: str
    key_seperator: str

    def __init__(
        self,
        redis: Redis,
        key_prefix: str = DEFAULT_KEY_PREFIX,
        key_seperator: str = DEFAULT_KEY_SEPERATOR,
    ) -> None:
        self.redis = redis
        self.key_prefix = key_prefix
        self.key_seperator = key_seperator

    @classmethod
    def from_pool(
        cls,
        pool: ConnectionPool,
        key_prefix: str = DEFAULT_KEY_PREFIX,
        key_seperator: str = DEFAULT_KEY_SEPERATOR,
    ) -> "RedisMailerStorage":
        redis = Redis.from_pool(connection_pool=pool)
        return cls(redis=redis, key_prefix=key_prefix, key_seperator=key_seperator)

    @classmethod
    def from_url(
        cls,
        url: str,
        key_prefix: str = DEFAULT_KEY_PREFIX,
        key_seperator: str = DEFAULT_KEY_SEPERATOR,
        **connection_options: Any,
    ) -> "RedisMailerStorage":
        connection_pool = ConnectionPool.from_url(url=url, **connection_options)
        redis = Redis.from_pool(connection_pool=connection_pool)
        return cls(redis=redis, key_prefix=key_prefix, key_seperator=key_seperator)

    async def get_mailer_ids(self) -> Set[int]:
        pattern = self.build_key()
        result = await self.redis.keys(pattern=pattern)
        return set(map(self.parse_key, result))

    async def get(self, mailer_id: int) -> StorageRecord:
        key = self.build_key(mailer_id=mailer_id)
        result = await self.redis.get(name=key)
        return StorageRecord.model_validate_json(json_data=result)

    async def set(self, mailer_id: int, record: StorageRecord) -> None:
        key = self.build_key(mailer_id=mailer_id)
        data = record.model_dump_json(exclude_defaults=True)
        await self.redis.set(name=key, value=data)

    async def delete(self, mailer_id: int) -> None:
        key = self.build_key(mailer_id=mailer_id)
        await self.redis.delete(key)

    def build_key(self, mailer_id: Optional[int] = None) -> str:
        pattern = (self.key_prefix, str(mailer_id or "*"))
        return self.key_seperator.join(pattern)

    def parse_key(self, key: Union[bytes, str]) -> int:
        key_string = key.decode() if isinstance(key, bytes) else key
        _, mailer_id = key_string.split(self.key_seperator)
        return int(mailer_id)

    async def startup(self) -> None:
        pass

    async def shutdown(self) -> None:
        await self.redis.aclose(close_connection_pool=True)
