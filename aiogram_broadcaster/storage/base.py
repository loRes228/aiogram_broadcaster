from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Set

from pydantic import BaseModel, ConfigDict, Field, JsonValue, SerializeAsAny

from aiogram_broadcaster.contents.base import BaseContent
from aiogram_broadcaster.mailer.chat_engine import ChatsRegistry
from aiogram_broadcaster.mailer.settings import MailerSettings


class StorageRecord(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    content: SerializeAsAny[BaseContent]
    chats: ChatsRegistry
    settings: MailerSettings
    bot_id: int
    context: Dict[str, SerializeAsAny[JsonValue]] = Field(default_factory=dict)


class BaseMailerStorage(ABC):
    @abstractmethod
    async def get_mailer_ids(self) -> Set[int]:
        pass

    @abstractmethod
    async def get(self, mailer_id: int) -> StorageRecord:
        pass

    @abstractmethod
    async def set(self, mailer_id: int, record: StorageRecord) -> None:
        pass

    @abstractmethod
    async def delete(self, mailer_id: int) -> None:
        pass

    @asynccontextmanager
    async def update(self, mailer_id: int) -> AsyncGenerator[StorageRecord, None]:
        record = await self.get(mailer_id=mailer_id)
        try:
            yield record
        finally:
            await self.set(mailer_id=mailer_id, record=record)

    @abstractmethod
    async def startup(self) -> None:
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        pass
