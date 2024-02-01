from typing import List, NamedTuple, Union

from redis.asyncio import ConnectionPool, Redis

from aiogram_broadcaster.data import Data

from .base import BaseStorage


class StorageKey(NamedTuple):
    chats: str
    settings: str


class RedisStorage(BaseStorage):
    redis: Redis
    key_prefix: str

    __slots__ = (
        "key_prefix",
        "redis",
    )

    def __init__(self, redis: Union[Redis, ConnectionPool], key_prefix: str = "BCR") -> None:
        self.redis = (
            Redis(connection_pool=redis)  # fmt: skip
            if isinstance(redis, ConnectionPool)
            else redis
        )
        if not self.redis.get_encoder().decode_responses:  # type: ignore[no-untyped-call]
            raise ValueError("The 'decode_responses' must be enabled in the Redis client.")
        self.key_prefix = key_prefix

    async def get_mailer_ids(self) -> List[int]:
        keys = await self.redis.keys(pattern=f"{self.key_prefix}:*:*")
        if not keys:
            return []
        return list({int(key.split(":")[1]) for key in keys})

    async def set_data(self, mailer_id: int, data: Data) -> None:
        key = self.build_key(mailer_id=mailer_id)
        await self.redis.rpush(key.chats, *data.chat_ids)  # type: ignore[misc]
        await self.redis.set(name=key.settings, value=data.settings.model_dump_json())

    async def get_data(self, mailer_id: int) -> Data:
        key = self.build_key(mailer_id=mailer_id)
        chats = await self.redis.lrange(name=key.chats, start=0, end=-1)  # type: ignore[misc]
        settings = await self.redis.get(name=key.settings)
        return Data.build_from_json(chat_ids=chats, settings=settings)

    async def delete_data(self, mailer_id: int) -> None:
        key = self.build_key(mailer_id=mailer_id)
        await self.redis.delete(key.chats, key.settings)

    async def pop_chat(self, mailer_id: int) -> None:
        key = self.build_key(mailer_id=mailer_id)
        await self.redis.lpop(name=key.chats)  # type: ignore[misc]

    def build_key(self, mailer_id: int) -> StorageKey:
        return StorageKey(
            chats=f"{self.key_prefix}:{mailer_id}:chats",
            settings=f"{self.key_prefix}:{mailer_id}:settings",
        )
