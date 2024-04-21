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

    def extract_mailer_ids(self, keys: Iterable[str]) -> Set[int]:
        mailer_ids = set()
        for key in keys:
            _, mailer_id = key.split(self.seperator)
            mailer_ids.add(int(mailer_id))
        return mailer_ids

    def build(self, mailer_id: int) -> str:
        key = (self.prefix, mailer_id)
        return self.seperator.join(map(str, key))


class RedisMailerStorage(BaseMailerStorage):
    redis: Redis
    key_builder: KeyBuilder

    def __init__(
        self,
        redis: Union[Redis, ConnectionPool],
        key_builder: Optional[KeyBuilder] = None,
    ) -> None:
        if isinstance(redis, ConnectionPool):
            redis = Redis(connection_pool=redis)
        self.redis = redis
        self.key_builder = key_builder or KeyBuilder()

        if not self.redis.get_encoder().decode_responses:  # type: ignore[no-untyped-call]
            raise RuntimeError("The 'decode_responses' must be set to True in the Redis client.")

    @classmethod
    def from_url(
        cls,
        url: str,
        key_builder: Optional[KeyBuilder] = None,
        **connection_options: Any,
    ) -> "RedisMailerStorage":
        connection_options["decode_responses"] = True
        pool = ConnectionPool.from_url(url=url, **connection_options)
        redis = Redis.from_pool(connection_pool=pool)
        return cls(redis=redis, key_builder=key_builder)

    async def get_mailer_ids(self) -> Set[int]:
        keys = await self.redis.keys(pattern=self.key_builder.pattern)
        return self.key_builder.extract_mailer_ids(keys=keys)

    async def get(self, mailer_id: int) -> StorageRecord:
        key = self.key_builder.build(mailer_id=mailer_id)
        data = await self.redis.get(name=key)
        return StorageRecord.model_validate_json(json_data=data)

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
