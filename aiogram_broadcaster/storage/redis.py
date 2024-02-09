from typing import List, NamedTuple, Union

from redis.asyncio import ConnectionPool, Redis

from aiogram_broadcaster.chat_manager import ChatState
from aiogram_broadcaster.settings import (
    ChatsSettings,
    MailerSettings,
    MessageSettings,
    Settings,
)

from .base import BaseMailerStorage


class StorageKey(NamedTuple):
    chats: str
    mailer: str
    message: str


class RedisMailerStorage(BaseMailerStorage):
    key_prefix: str
    redis: Redis

    __slots__ = (
        "key_prefix",
        "redis",
    )

    def __init__(
        self,
        redis: Union[Redis, ConnectionPool],
        key_prefix: str = "bcr",
    ) -> None:
        self.key_prefix = key_prefix

        if isinstance(redis, ConnectionPool):
            redis = Redis(connection_pool=redis)
        self.redis = redis

        if not redis.get_encoder().decode_responses:  # type: ignore[no-untyped-call]
            raise ValueError("The 'decode_responses' must be enabled in the Redis client.")

    async def get_mailer_ids(self) -> List[int]:
        keys = await self.redis.keys(pattern=f"{self.key_prefix}:*:*")
        if not keys:
            return []
        mailer_ids = [key.split(":")[1] for key in keys]
        return list(map(int, set(mailer_ids)))

    async def delete_settings(self, mailer_id: int) -> None:
        key = self.build_key(mailer_id=mailer_id)
        await self.redis.delete(
            key.chats,
            key.mailer,
            key.message,
        )

    async def get_settings(self, mailer_id: int) -> Settings:
        key = self.build_key(mailer_id=mailer_id)
        chats = await self.redis.hgetall(name=key.chats)  # type: ignore[misc]
        mailer = await self.redis.get(name=key.mailer)
        message = await self.redis.get(name=key.message)
        return Settings(
            chats=ChatsSettings(chats=chats),
            mailer=MailerSettings.model_validate_json(mailer),
            message=MessageSettings.model_validate_json(message),
        )

    async def set_settings(
        self,
        mailer_id: int,
        settings: Settings,
    ) -> None:
        key = self.build_key(mailer_id=mailer_id)
        await self.redis.hset(  # type: ignore[misc]
            name=key.chats,
            mapping=settings.chats.chats,
        )
        await self.redis.set(
            name=key.mailer,
            value=settings.mailer.model_dump_json(
                exclude_unset=True,
                exclude_defaults=True,
                exclude_none=True,
            ),
        )
        await self.redis.set(
            name=key.message,
            value=settings.message.model_dump_json(
                exclude_unset=True,
                exclude_defaults=True,
                exclude_none=True,
            ),
        )

    async def set_chat_state(
        self,
        mailer_id: int,
        chat: int,
        state: ChatState,
    ) -> None:
        key = self.build_key(mailer_id=mailer_id)
        await self.redis.hset(  # type: ignore[misc]
            name=key.chats,
            key=str(chat),
            value=str(state.value),
        )

    def build_key(self, mailer_id: int) -> StorageKey:
        prefix = f"{self.key_prefix}:{mailer_id}"
        return StorageKey(
            chats=f"{prefix}:chats",
            mailer=f"{prefix}:mailer",
            message=f"{prefix}:message",
        )
