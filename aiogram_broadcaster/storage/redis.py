from typing import Any, Iterable, Optional, Set, Union

from redis.asyncio import ConnectionPool, Redis

from .base import BaseMailerStorage, StorageRecord


class KeyBuilder:
    prefix: str
    seperator: str

    def __init__(
        self,
        prefix: str = "bcr",
        seperator: str = ":",
    ) -> None:
        self.prefix = prefix
        self.seperator = seperator

    @property
    def pattern(self) -> str:
        pattern = (self.prefix, "*")
        return self.seperator.join(pattern)

    def extract_mailer_ids(self, keys: Iterable[Union[bytes, str]]) -> Set[int]:
        mailer_ids = set()
        for key in keys:
            key_string = key.decode() if isinstance(key, bytes) else key
            _, mailer_id = key_string.split(self.seperator)
            mailer_ids.add(int(mailer_id))
        return mailer_ids

    def build(self, mailer_id: int) -> str:
        key = (self.prefix, mailer_id)
        return self.seperator.join(map(str, key))


class RedisMailerStorage(BaseMailerStorage):
    redis: Redis
    key_builder: KeyBuilder

    def __init__(self, redis: Redis, key_builder: Optional[KeyBuilder] = None) -> None:
        self.redis = redis
        self.key_builder = key_builder or KeyBuilder()

    @classmethod
    def from_pool(
        cls,
        pool: ConnectionPool,
        key_builder: Optional[KeyBuilder] = None,
    ) -> "RedisMailerStorage":
        redis = Redis.from_pool(connection_pool=pool)
        return cls(redis=redis, key_builder=key_builder)

    @classmethod
    def from_url(
        cls,
        url: str,
        key_builder: Optional[KeyBuilder] = None,
        **connection_options: Any,
    ) -> "RedisMailerStorage":
        connection_pool = ConnectionPool.from_url(url=url, **connection_options)
        redis = Redis.from_pool(connection_pool=connection_pool)
        return cls(redis=redis, key_builder=key_builder)

    async def get_mailer_ids(self) -> Set[int]:
        result = await self.redis.keys(pattern=self.key_builder.pattern)
        return self.key_builder.extract_mailer_ids(keys=result)

    async def get(self, mailer_id: int) -> StorageRecord:
        key = self.key_builder.build(mailer_id=mailer_id)
        result = await self.redis.get(name=key)
        return StorageRecord.model_validate_json(json_data=result)

    async def set(self, mailer_id: int, record: StorageRecord) -> None:
        key = self.key_builder.build(mailer_id=mailer_id)
        data = record.model_dump_json(exclude_defaults=True)
        await self.redis.set(name=key, value=data)

    async def delete(self, mailer_id: int) -> None:
        key = self.key_builder.build(mailer_id=mailer_id)
        await self.redis.delete(key)

    async def startup(self) -> None:
        pass

    async def shutdown(self) -> None:
        await self.redis.aclose(close_connection_pool=True)
