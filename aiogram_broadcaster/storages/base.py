from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, AsyncIterable
from contextlib import asynccontextmanager
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, JsonValue, SerializeAsAny

from aiogram_broadcaster.contents.base import BaseContent
from aiogram_broadcaster.intervals.base import BaseInterval
from aiogram_broadcaster.mailer.chats import Chats


class StorageRecord(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    chats: Chats
    content: SerializeAsAny[BaseContent]
    interval: Optional[SerializeAsAny[BaseInterval]] = None
    bot_id: int
    context: dict[str, JsonValue] = Field(default_factory=dict)


class BaseStorage(ABC):
    @asynccontextmanager
    async def update_record(self, mailer_id: int) -> AsyncGenerator[StorageRecord, None]:
        record = await self.get_record(mailer_id=mailer_id)
        try:
            yield record
        finally:
            await self.set_record(mailer_id=mailer_id, record=record)

    @abstractmethod
    def get_records(self) -> AsyncIterable[tuple[int, StorageRecord]]:
        pass

    @abstractmethod
    async def set_record(self, mailer_id: int, record: StorageRecord) -> None:
        pass

    @abstractmethod
    async def get_record(self, mailer_id: int) -> StorageRecord:
        pass

    @abstractmethod
    async def delete_record(self, mailer_id: int) -> None:
        pass

    @abstractmethod
    async def startup(self) -> None:
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        pass
