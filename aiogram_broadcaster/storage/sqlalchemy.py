from typing import Any, Dict, Optional, Set, Union, cast

from sqlalchemy import (
    URL,
    BigInteger,
    Column,
    MetaData,
    String,
    Table,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .base import BaseMailerStorage, StorageRecord


DEFAULT_TABLE_NAME = "mailers"


class SQLAlchemyMailerStorage(BaseMailerStorage):
    session_maker: async_sessionmaker[AsyncSession]
    table_name: str
    table: Table

    def __init__(
        self,
        session_maker: async_sessionmaker[AsyncSession],
        table_name: str = DEFAULT_TABLE_NAME,
    ) -> None:
        self.session_maker = session_maker
        self.table_name = table_name

        self.table = Table(
            self.table_name,
            MetaData(),
            Column("id", BigInteger(), index=True, unique=True, nullable=False, primary_key=True),
            Column("data", String(), nullable=False),
        )

    @classmethod
    def from_engine(
        cls,
        engine: AsyncEngine,
        table_name: str = DEFAULT_TABLE_NAME,
        **session_options: Any,
    ) -> "SQLAlchemyMailerStorage":
        session_maker = async_sessionmaker(bind=engine, **session_options)
        return cls(session_maker=session_maker, table_name=table_name)

    @classmethod
    def from_url(
        cls,
        url: Union[str, URL],
        table_name: str = DEFAULT_TABLE_NAME,
        engine_options: Optional[Dict[str, Any]] = None,
        session_options: Optional[Dict[str, Any]] = None,
    ) -> "SQLAlchemyMailerStorage":
        engine = create_async_engine(url=url, **(engine_options or {}))
        session_maker = async_sessionmaker(bind=engine, **(session_options or {}))
        return cls(session_maker=session_maker, table_name=table_name)

    @property
    def engine(self) -> AsyncEngine:
        return cast(AsyncEngine, self.session_maker.kw["bind"])

    async def get_mailer_ids(self) -> Set[int]:
        statement = select(self.table.c.id)
        async with self.session_maker() as session:
            result = await session.execute(statement=statement)
        return set(result.scalars().all())

    async def get(self, mailer_id: int) -> StorageRecord:
        statement = select(self.table.c.data).where(self.table.c.id == mailer_id)
        async with self.session_maker() as session:
            result = await session.execute(statement=statement)
        return StorageRecord.model_validate_json(json_data=result.scalar_one())

    async def set(self, mailer_id: int, record: StorageRecord) -> None:
        data = record.model_dump_json(exclude_defaults=True)
        insert_statement = insert(self.table).values(id=mailer_id, data=data)
        update_statement = update(self.table).where(self.table.c.id == mailer_id).values(data=data)
        async with self.session_maker() as session:
            try:
                await session.execute(statement=insert_statement)
            except IntegrityError:
                await session.rollback()
                await session.execute(statement=update_statement)
            await session.commit()

    async def delete(self, mailer_id: int) -> None:
        statement = delete(self.table).where(self.table.c.id == mailer_id)
        async with self.session_maker() as session:
            await session.execute(statement=statement)
            await session.commit()

    async def startup(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(self.table.create, checkfirst=True)

    async def shutdown(self) -> None:
        await self.engine.dispose(close=True)
