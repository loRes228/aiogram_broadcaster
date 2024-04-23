from typing import Any, Set

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from .base import BaseMailerStorage, StorageRecord


DEFAULT_DATABASE_NAME = "broadcaster"
DEFAULT_COLLECTION_NAME = "mailers"


class MongoDBMailerStorage(BaseMailerStorage):
    client: AsyncIOMotorClient
    database_name: str
    collection_name: str
    collection: AsyncIOMotorCollection

    def __init__(
        self,
        client: AsyncIOMotorClient,
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
        database_name: str = DEFAULT_DATABASE_NAME,
        collection_name: str = DEFAULT_COLLECTION_NAME,
        **client_options: Any,
    ) -> "MongoDBMailerStorage":
        client = AsyncIOMotorClient(url, **client_options)
        return cls(client=client, database_name=database_name, collection_name=collection_name)

    async def get_mailer_ids(self) -> Set[int]:
        result = await self.collection.distinct(key="_id")
        return set(result)

    async def get(self, mailer_id: int) -> StorageRecord:
        result = await self.collection.find_one(filter={"_id": mailer_id})
        if not result:
            raise LookupError("Document not found.")
        return StorageRecord(**result)

    async def set(self, mailer_id: int, record: StorageRecord) -> None:
        data = record.model_dump(mode="json", exclude_defaults=True)
        await self.collection.update_one(
            filter={"_id": mailer_id},
            update={"$set": data},
            upsert=True,
        )

    async def delete(self, mailer_id: int) -> None:
        await self.collection.delete_one(filter={"_id": mailer_id})

    async def startup(self) -> None:
        pass

    async def shutdown(self) -> None:
        self.client.close()
