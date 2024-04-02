from asyncio import Lock
from json import dumps, loads
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Set, Union, cast

from aiofiles import open

from .base import BaseBCRStorage
from .record import StorageRecord


JsonLoads = Callable[..., Any]
JsonDumps = Callable[..., str]


class FileBCRStorage(BaseBCRStorage):
    file: Path
    json_loads: JsonLoads
    json_dumps: JsonDumps
    _lock: Optional[Lock]

    def __init__(
        self,
        filename: Union[str, Path] = ".mailers.json",
        json_loads: JsonLoads = loads,
        json_dumps: JsonDumps = dumps,
    ) -> None:
        if not isinstance(filename, Path):
            filename = Path(filename)
        self.file = filename
        self.json_loads = json_loads
        self.json_dumps = json_dumps
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
        return set(map(int, records))

    async def get_record(self, mailer_id: int) -> StorageRecord:
        records = await self.get_records()
        return StorageRecord.model_validate(
            obj=records[str(mailer_id)],
            context={"mailer_id": mailer_id, "storage": self},
        )

    async def set_record(self, mailer_id: int, record: StorageRecord) -> None:
        records = await self.get_records()
        records[str(mailer_id)] = record.model_dump(mode="json", exclude_defaults=True)
        await self.set_records(data=records)

    async def delete_record(self, mailer_id: int) -> None:
        records = await self.get_records()
        del records[str(mailer_id)]
        await self.set_records(data=records)

    async def get_records(self) -> Dict[str, Any]:
        if not self.file.exists() or self.file.stat().st_size == 0:
            await self.set_records(data={})
            return {}
        async with open(file=self.file, encoding="utf-8") as file:
            data = await file.read()
            json_data = self.json_loads(data)
            return cast(Dict[str, Any], json_data)

    async def set_records(self, data: Dict[str, Any]) -> None:
        async with open(file=self.file, mode="w", encoding="utf-8") as file:
            json_data = self.json_dumps(data)
            await file.write(json_data)

    async def close(self) -> None:
        pass
