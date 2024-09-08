from collections.abc import AsyncIterable, Mapping
from typing import Any, Optional, Union

from typing_extensions import Self

from aiogram_broadcaster.utils.exceptions import DependencyNotFoundError

from .base import BaseStorage, StorageRecord


try:
    from redis.asyncio import ConnectionPool, Redis
except ImportError as error:
    raise DependencyNotFoundError(
        feature_name="RedisStorage",
        module_name="redis",
        extra_name="redis",
    ) from error


DEFAULT_KEY_PREFIX = "mailer"
DEFAULT_KEY_SEPERATOR = ":"


class RedisStorage(BaseStorage):
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
    def from_connection_pool(
        cls,
        connection_pool: ConnectionPool,
        key_prefix: str = DEFAULT_KEY_PREFIX,
        key_seperator: str = DEFAULT_KEY_SEPERATOR,
    ) -> Self:
        redis = Redis.from_pool(connection_pool=connection_pool)
        return cls(redis=redis, key_prefix=key_prefix, key_seperator=key_seperator)

    @classmethod
    def from_url(
        cls,
        url: str,
        connection_options: Optional[Mapping[str, Any]] = None,
        key_prefix: str = DEFAULT_KEY_PREFIX,
        key_seperator: str = DEFAULT_KEY_SEPERATOR,
    ) -> Self:
        connection_pool = ConnectionPool.from_url(url=url, **(connection_options or {}))
        redis = Redis(connection_pool=connection_pool)
        return cls(redis=redis, key_prefix=key_prefix, key_seperator=key_seperator)

    async def get_records(self) -> AsyncIterable[tuple[int, StorageRecord]]:
        pattern = self.build_key()
        keys = await self.redis.keys(pattern=pattern)
        for mailer_id in map(self.parse_key, keys):
            yield mailer_id, await self.get_record(mailer_id=mailer_id)

    async def set_record(self, mailer_id: int, record: StorageRecord) -> None:
        key = self.build_key(mailer_id=mailer_id)
        data = record.model_dump_json(exclude_defaults=True)
        await self.redis.set(name=key, value=data)

    async def get_record(self, mailer_id: int) -> StorageRecord:
        key = self.build_key(mailer_id=mailer_id)
        data = await self.redis.get(name=key)
        return StorageRecord.model_validate_json(json_data=data)

    async def delete_record(self, mailer_id: int) -> None:
        key = self.build_key(mailer_id=mailer_id)
        await self.redis.delete(key)

    async def startup(self) -> None:
        pass

    async def shutdown(self) -> None:
        await self.redis.aclose(close_connection_pool=True)

    def build_key(self, mailer_id: Optional[int] = None) -> str:
        key = (self.key_prefix, str(mailer_id or "*"))
        return self.key_seperator.join(key)

    def parse_key(self, key: Union[bytes, str]) -> int:
        key_string = key.decode() if isinstance(key, bytes) else key
        _, mailer_id = key_string.split(self.key_seperator)
        return int(mailer_id)
