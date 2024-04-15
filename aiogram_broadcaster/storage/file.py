from asyncio import Lock
from pathlib import Path
from typing import Any, Dict, Optional, Set, Union

from aiofiles import open
from pydantic import BaseModel, Field

from .base import BaseBCRStorage
from .record import StorageRecord


class StorageRecords(BaseModel):
    records: Dict[int, Any] = Field(default_factory=dict)


class FileBCRStorage(BaseBCRStorage):
    file: Path
    _lock: Optional[Lock]

    def __init__(self, filename: Union[str, Path] = ".mailers.json") -> None:
        if not isinstance(filename, Path):
            filename = Path(filename)
        self.file = filename
        self._lock = None

        if self.file.exists() and not self.file.is_file():
            raise RuntimeError("The filename is not a file.")

    @property
    def lock(self) -> Lock:
        """Lazy initialization to correctly catch the event loop."""
        if self._lock is None:
            self._lock = Lock()
        return self._lock

    async def get_mailer_ids(self) -> Set[int]:
        async with self.lock:
            records = await self.get_records()
            return set(records.records)

    async def get(self, mailer_id: int) -> StorageRecord:
        async with self.lock:
            records = await self.get_records()
            return StorageRecord.model_validate(
                obj=records.records[mailer_id],
                context={"mailer_id": mailer_id, "storage": self},
            )

    async def set(self, mailer_id: int, record: StorageRecord) -> None:
        async with self.lock:
            records = await self.get_records()
            records.records[mailer_id] = record.model_dump(mode="json", exclude_defaults=True)
            await self.set_records(records=records)

    async def delete(self, mailer_id: int) -> None:
        async with self.lock:
            records = await self.get_records()
            del records.records[mailer_id]
            await self.set_records(records=records)

    async def get_records(self) -> StorageRecords:
        if not self.file.exists() or self.file.stat().st_size == 0:
            records = StorageRecords()
            await self.set_records(records=records)
            return records
        async with open(file=self.file, mode="r", encoding="utf-8") as file:
            data = await file.read()
            return StorageRecords.model_validate_json(json_data=data)

    async def set_records(self, records: StorageRecords) -> None:
        async with open(file=self.file, mode="w", encoding="utf-8") as file:
            data = records.model_dump_json(exclude_defaults=True)
            await file.write(data)

    async def close(self) -> None:
        pass
