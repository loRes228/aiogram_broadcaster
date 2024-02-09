from typing import Any, Dict, List, Literal, Optional, Union

from redis.asyncio import ConnectionPool, Redis

from aiogram_broadcaster.chat_manager import ChatState
from aiogram_broadcaster.settings import (
    ChatsSettings,
    MailerSettings,
    MessageSettings,
    Settings,
)

from .base import BaseMailerStorage


class KeyBuilder:
    def __init__(
        self,
        prefix: str = "bcr",
        seperator: str = ":",
    ) -> None:
        self.prefix = prefix
        self.seperator = seperator

    @property
    def pattern(self) -> str:
        pattern = (self.prefix, "*", "*")
        return self.seperator.join(pattern)

    def extract_mailer_ids(self, raw_keys: List[str]) -> List[int]:
        mailer_ids = set()
        for raw_key in raw_keys:
            _, mailer_id, _ = raw_key.split(self.seperator)
            mailer_ids.add(int(mailer_id))
        return list(mailer_ids)

    def build_keys(self, mailer_id: int) -> List[str]:
        return [
            self.build(mailer_id=mailer_id, part=part)  # type: ignore[arg-type]
            for part in ("chats", "mailer", "message")
        ]

    def build(
        self,
        mailer_id: int,
        part: Literal["chats", "mailer", "message"],
    ) -> str:
        key = (self.prefix, str(mailer_id), part)
        return self.seperator.join(key)


class RedisMailerStorage(BaseMailerStorage):
    key_builder: KeyBuilder
    redis: Redis

    __slots__ = (
        "key_builder",
        "redis",
    )

    def __init__(
        self,
        redis: Union[Redis, ConnectionPool],
        key_builder: Optional[KeyBuilder] = None,
    ) -> None:
        self.key_builder = key_builder or KeyBuilder()

        if isinstance(redis, ConnectionPool):
            redis = Redis(connection_pool=redis)
        self.redis = redis

        if not redis.get_encoder().decode_responses:  # type: ignore[no-untyped-call]
            raise ValueError("The 'decode_responses' must be enabled in the Redis client.")

    @classmethod
    def from_url(
        cls,
        url: str,
        connection_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> "RedisMailerStorage":
        if not connection_kwargs:
            connection_kwargs = {}
        connection_kwargs["decode_responses"] = True
        pool = ConnectionPool.from_url(url=url, **connection_kwargs)
        return RedisMailerStorage(redis=pool, **kwargs)

    async def get_mailer_ids(self) -> List[int]:
        keys = await self.redis.keys(pattern=self.key_builder.pattern)
        if not keys:
            return []
        return self.key_builder.extract_mailer_ids(raw_keys=keys)

    async def delete(self, mailer_id: int) -> None:
        keys = self.key_builder.build_keys(mailer_id=mailer_id)
        await self.redis.delete(*keys)

    async def get(self, mailer_id: int) -> Settings:
        return Settings(
            chats=await self.get_chats(mailer_id=mailer_id),
            mailer=await self.get_mailer(mailer_id=mailer_id),
            message=await self.get_message(mailer_id=mailer_id),
        )

    async def set(self, mailer_id: int, settings: Settings) -> None:
        await self.set_chats(
            mailer_id=mailer_id,
            settings=settings.chats,
        )
        await self.set_mailer(
            mailer_id=mailer_id,
            settings=settings.mailer,
        )
        await self.set_message(
            mailer_id=mailer_id,
            settings=settings.message,
        )

    async def get_chats(self, mailer_id: int) -> ChatsSettings:
        key = self.key_builder.build(
            mailer_id=mailer_id,
            part="chats",
        )
        chats = await self.redis.hgetall(name=key)  # type: ignore[misc]
        return ChatsSettings(chats=chats)

    async def get_mailer(self, mailer_id: int) -> MailerSettings:
        key = self.key_builder.build(
            mailer_id=mailer_id,
            part="mailer",
        )
        mailer = await self.redis.get(name=key)
        return MailerSettings.model_validate_json(json_data=mailer)

    async def get_message(self, mailer_id: int) -> MessageSettings:
        key = self.key_builder.build(
            mailer_id=mailer_id,
            part="message",
        )
        message = await self.redis.get(name=key)
        return MessageSettings.model_validate_json(json_data=message)

    async def set_chats(self, mailer_id: int, settings: ChatsSettings) -> None:
        key = self.key_builder.build(
            mailer_id=mailer_id,
            part="chats",
        )
        await self.redis.hset(  # type: ignore[misc]
            name=key,
            mapping=settings.chats,
        )

    async def set_mailer(self, mailer_id: int, settings: MailerSettings) -> None:
        key = self.key_builder.build(
            mailer_id=mailer_id,
            part="mailer",
        )
        await self.redis.set(
            name=key,
            value=settings.model_dump_json(
                exclude_unset=True,
                exclude_defaults=True,
                exclude_none=True,
            ),
        )

    async def set_message(self, mailer_id: int, settings: MessageSettings) -> None:
        key = self.key_builder.build(
            mailer_id=mailer_id,
            part="message",
        )
        await self.redis.set(
            name=key,
            value=settings.model_dump_json(
                exclude_unset=True,
                exclude_defaults=True,
                exclude_none=True,
            ),
        )

    async def set_chat_state(self, mailer_id: int, chat: int, state: ChatState) -> None:
        key = self.key_builder.build(
            mailer_id=mailer_id,
            part="chats",
        )
        await self.redis.hset(  # type: ignore[misc]
            name=key,
            key=str(chat),
            value=str(state.value),
        )
