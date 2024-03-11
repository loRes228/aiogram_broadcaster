from typing import Any, Iterable, List, Literal, Optional, Set, Union

from redis.asyncio import ConnectionPool, Redis

from aiogram_broadcaster.contents import BaseContent
from aiogram_broadcaster.mailer.chat_manager import ChatManager, ChatState
from aiogram_broadcaster.mailer.settings import MailerSettings

from .base import BaseBCRStorage


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
        pattern = (self.prefix, "*", "*")
        return self.seperator.join(pattern)

    def extract_mailer_ids(self, keys: Iterable[str]) -> Set[int]:
        mailer_ids = set()
        for key in keys:
            _, mailer_id, _ = key.split(self.seperator)
            mailer_ids.add(int(mailer_id))
        return mailer_ids

    def build_keys(self, mailer_id: int) -> List[str]:
        return [
            self.build(mailer_id=mailer_id, part=part)  # type: ignore[arg-type]
            for part in ["content", "chats", "settings", "bot"]
        ]

    def build(
        self,
        mailer_id: int,
        part: Literal["content", "chats", "settings", "bot"],
    ) -> str:
        pattern = (self.prefix, mailer_id, part)
        return self.seperator.join(map(str, pattern))


class RedisBCRStorage(BaseBCRStorage):
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
            raise RuntimeError("'decode_responses' must be set to True in the Redis client.")

    @classmethod
    def from_url(
        cls,
        url: str,
        key_builder: Optional[KeyBuilder] = None,
        **connection_kwargs: Any,
    ) -> "RedisBCRStorage":
        connection_kwargs["decode_responses"] = True
        redis = Redis.from_url(url=url, **connection_kwargs)
        return RedisBCRStorage(redis=redis, key_builder=key_builder)

    async def get_mailer_ids(self) -> Set[int]:
        keys = await self.redis.keys(pattern=self.key_builder.pattern)
        return self.key_builder.extract_mailer_ids(keys=keys)

    async def delete(self, mailer_id: int) -> None:
        keys = self.key_builder.build_keys(mailer_id=mailer_id)
        await self.redis.delete(*keys)

    async def migrate_keys(self, old_mailer_id: int, new_mailer_id: int) -> None:
        old_keys = self.key_builder.build_keys(mailer_id=old_mailer_id)
        new_keys = self.key_builder.build_keys(mailer_id=new_mailer_id)
        for old_key, new_key in zip(old_keys, new_keys):
            await self.redis.rename(src=old_key, dst=new_key)

    async def get_content(self, mailer_id: int) -> BaseContent:
        key = self.key_builder.build(mailer_id=mailer_id, part="content")
        data = await self.redis.get(name=key)
        return BaseContent.model_validate_json(json_data=data)

    async def set_content(self, mailer_id: int, content: BaseContent) -> None:
        key = self.key_builder.build(mailer_id=mailer_id, part="content")
        data = content.model_dump_json(exclude_defaults=True)
        await self.redis.set(name=key, value=data)

    async def get_chats(self, mailer_id: int) -> ChatManager:
        key = self.key_builder.build(mailer_id=mailer_id, part="chats")
        data = await self.redis.hgetall(name=key)  # type: ignore[misc]
        return ChatManager.from_mapping(mapping=data, mailer_id=mailer_id, storage=self)

    async def set_chats(self, mailer_id: int, chats: ChatManager) -> None:
        key = self.key_builder.build(mailer_id=mailer_id, part="chats")
        data = chats.to_dict()
        await self.redis.hset(name=key, mapping=data)  # type: ignore[misc]

    async def set_chat_state(self, mailer_id: int, chat: int, state: ChatState) -> None:
        key = self.key_builder.build(mailer_id=mailer_id, part="chats")
        await self.redis.hset(name=key, key=str(chat), value=str(state.value))  # type: ignore[misc]

    async def get_settings(self, mailer_id: int) -> MailerSettings:
        key = self.key_builder.build(mailer_id=mailer_id, part="settings")
        data = await self.redis.get(name=key)
        return MailerSettings.model_validate_json(json_data=data)

    async def set_settings(self, mailer_id: int, settings: MailerSettings) -> None:
        key = self.key_builder.build(mailer_id=mailer_id, part="settings")
        data = settings.model_dump_json(exclude_defaults=True)
        await self.redis.set(name=key, value=data)

    async def get_bot(self, mailer_id: int) -> int:
        key = self.key_builder.build(mailer_id=mailer_id, part="bot")
        return int(await self.redis.get(name=key))

    async def set_bot(self, mailer_id: int, bot: int) -> None:
        key = self.key_builder.build(mailer_id=mailer_id, part="bot")
        await self.redis.set(name=key, value=bot)
