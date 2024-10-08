from asyncio import Lock
from collections.abc import AsyncIterable
from os import PathLike
from pathlib import Path
from typing import Any, Optional, Union

from aiofiles import open
from pydantic import BaseModel, ConfigDict, Field

from .base import BaseStorage, StorageRecord


class StorageRecords(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    records: dict[int, Any] = Field(default_factory=dict)


class FileStorage(BaseStorage):
    def __init__(self, filename: Union[str, PathLike[str], Path] = ".mailers.json") -> None:
        self.file = Path(filename)
        self._lock: Optional[Lock] = None

    @property
    def lock(self) -> Lock:
        if not self._lock:
            self._lock = Lock()
        return self._lock

    async def get_records(self) -> AsyncIterable[tuple[int, StorageRecord]]:
        async with self.lock:
            records = await self.read_records()
            for mailer_id, record in records.records.items():
                yield mailer_id, StorageRecord.model_validate(obj=record)

    async def set_record(self, mailer_id: int, record: StorageRecord) -> None:
        async with self.lock:
            records = await self.read_records()
            records.records[mailer_id] = record.model_dump(mode="json", exclude_defaults=True)
            await self.write_records(records=records)

    async def get_record(self, mailer_id: int) -> StorageRecord:
        async with self.lock:
            records = await self.read_records()
            return StorageRecord.model_validate(obj=records.records[mailer_id])

    async def delete_record(self, mailer_id: int) -> None:
        async with self.lock:
            records = await self.read_records()
            del records.records[mailer_id]
            await self.write_records(records=records)

    async def startup(self) -> None:
        if self.file.exists():
            if not self.file.is_file():
                raise RuntimeError(f"The file '{self.file.name}' is not a file.")
            if self.file.stat().st_size > 0:
                return
        records = StorageRecords()
        await self.write_records(records=records)

    async def shutdown(self) -> None:
        pass

    async def read_records(self) -> StorageRecords:
        async with open(file=self.file, encoding="utf-8") as file:
            data = await file.read()
            return StorageRecords.model_validate_json(json_data=data)

    async def write_records(self, records: StorageRecords) -> None:
        async with open(file=self.file, mode="w", encoding="utf-8") as file:
            data = records.model_dump_json(exclude_defaults=True)
            await file.write(data)
