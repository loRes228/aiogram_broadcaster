from typing import List, NamedTuple

from redis.asyncio import Redis

from .models import MailerData


class StorageKey(NamedTuple):
    chats: str
    settings: str


class MailerStorage:
    redis: Redis
    key_prefix: str

    __slots__ = (
        "redis",
        "key_prefix",
    )

    def __init__(self, redis: Redis, key_prefix: str) -> None:
        self.redis = redis
        self.key_prefix = key_prefix

    async def get_mailer_ids(self) -> List[int]:
        keys = await self.redis.keys(pattern=f"{self.key_prefix}:*:*")
        if not keys:
            return []
        return list({int(key.split(":")[1]) for key in keys})

    async def get_data(self, mailer_id: int) -> MailerData:
        key = self.build_key(mailer_id=mailer_id)
        chats = await self.redis.lrange(name=key.chats, start=0, end=-1)  # type: ignore[misc]
        settings = await self.redis.get(name=key.settings)
        return MailerData.build_from_json(chat_ids=chats, settings=settings)

    async def set_data(self, mailer_id: int, data: MailerData) -> None:
        key = self.build_key(mailer_id=mailer_id)
        await self.redis.rpush(key.chats, *data.chat_ids)  # type: ignore[misc]
        await self.redis.set(name=key.settings, value=data.settings.model_dump_json())

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
