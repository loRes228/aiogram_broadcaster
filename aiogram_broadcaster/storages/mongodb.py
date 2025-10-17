from collections.abc import AsyncIterable, Mapping
from typing import TYPE_CHECKING, Any, Optional

from typing_extensions import Self

from .base import BaseStorage, StorageRecord


if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorClient
    from pymongo import AsyncMongoClient


DEFAULT_DATABASE_NAME = "aiogram_broadcaster"
DEFAULT_COLLECTION_NAME = "mailers"


class MongoDBStorage(BaseStorage):
    def __init__(
        self,
        client: "AsyncMongoClient | AsyncIOMotorClient",
        database_name: str = DEFAULT_DATABASE_NAME,
        collection_name: str = DEFAULT_COLLECTION_NAME,
    ) -> None:
        self.client = client
        self.database_name = database_name
        self.collection_name = collection_name
        self.collection = self.client[self.database_name][self.collection_name]

    @classmethod
    def from_url(
        cls,
        url: str,
        client_class: "type[AsyncMongoClient | AsyncIOMotorClient]",
        client_options: Optional[Mapping[str, Any]] = None,
        database_name: str = DEFAULT_DATABASE_NAME,
        collection_name: str = DEFAULT_COLLECTION_NAME,
    ) -> Self:
        client = client_class(host=url, **(client_options or {}))
        return cls(client=client, database_name=database_name, collection_name=collection_name)

    async def get_records(self) -> AsyncIterable[tuple[int, StorageRecord]]:
        async for document in self.collection.find():
            yield document["_id"], StorageRecord.model_validate(obj=document)

    async def set_record(self, mailer_id: int, record: StorageRecord) -> None:
        data = record.model_dump(mode="json", exclude_defaults=True)
        await self.collection.update_one(
            filter={"_id": mailer_id},
            update={"$set": data},
            upsert=True,
        )

    async def get_record(self, mailer_id: int) -> StorageRecord:
        document = await self.collection.find_one(filter={"_id": mailer_id})
        if not document:
            raise LookupError
        return StorageRecord.model_validate(obj=document)

    async def delete_record(self, mailer_id: int) -> None:
        await self.collection.delete_one(filter={"_id": mailer_id})

    async def startup(self) -> None:
        pass

    async def shutdown(self) -> None:
        self.client.close()
