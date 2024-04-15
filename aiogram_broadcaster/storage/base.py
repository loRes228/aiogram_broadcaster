from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, AsyncGenerator, Set


if TYPE_CHECKING:
    from .record import StorageRecord


class BaseBCRStorage(ABC):
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
    async def close(self) -> None:
        pass
