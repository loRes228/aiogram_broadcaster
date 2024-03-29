from asyncio import Lock
from pathlib import Path
from typing import Any, Dict, Optional, Set, Union

from aiofiles import open
from pydantic import BaseModel, Field

from .base import BaseBCRStorage
from .record import StorageRecord


class StorageRecords(BaseModel):
    records: Dict[int, StorageRecord] = Field(default_factory=dict)


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
        records = await self.get_records()
        return set(records.records)

    async def get_record(self, mailer_id: int) -> StorageRecord:
        records = await self.get_records(mailer_id=mailer_id, storage=self)
        return records.records[mailer_id]

    async def set_record(self, mailer_id: int, record: StorageRecord) -> None:
        records = await self.get_records()
        records.records[mailer_id] = record
        await self.set_records(records=records)

    async def delete_record(self, mailer_id: int) -> None:
        records = await self.get_records()
        del records.records[mailer_id]
        await self.set_records(records=records)

    async def get_records(self, **pydantic_context: Any) -> StorageRecords:
        if not self.file.exists() or self.file.stat().st_size == 0:
            records = StorageRecords()
            await self.set_records(records=records)
            return records
        async with self.lock, open(file=self.file, mode="r", encoding="utf-8") as file:
            data = await file.read()
            return StorageRecords.model_validate_json(
                json_data=data,
                context=pydantic_context,
            )

    async def set_records(self, records: StorageRecords) -> None:
        async with self.lock, open(file=self.file, mode="w", encoding="utf-8") as file:
            data = records.model_dump_json(exclude_defaults=True)
            await file.write(data)

    async def close(self) -> None:
        pass
