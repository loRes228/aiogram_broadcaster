from collections.abc import AsyncIterable, Mapping
from typing import Any, Optional, Union, cast

from typing_extensions import Self

from aiogram_broadcaster.utils.exceptions import DependencyNotFoundError

from .base import BaseStorage, StorageRecord


try:
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
except ImportError as error:
    raise DependencyNotFoundError(
        feature_name="SQLAlchemyStorage",
        module_name="sqlalchemy",
        extra_name="sqlalchemy",
    ) from error


DEFAULT_TABLE_NAME = "aiogram_broadcaster"


class SQLAlchemyStorage(BaseStorage):
    def __init__(
        self,
        session_maker: async_sessionmaker[AsyncSession],
        table_name: str = DEFAULT_TABLE_NAME,
    ) -> None:
        self.session_maker = session_maker
        self.table_name = table_name

        self.table = Table(
            table_name,
            MetaData(),
            Column(
                "id",
                BigInteger(),
                index=True,
                unique=True,
                nullable=False,
                primary_key=True,
            ),
            Column(
                "data",
                String(),
                nullable=False,
            ),
        )

    @classmethod
    def from_engine(
        cls,
        engine: AsyncEngine,
        session_options: Optional[Mapping[str, Any]] = None,
        table_name: str = DEFAULT_TABLE_NAME,
    ) -> Self:
        session_maker = async_sessionmaker(bind=engine, **(session_options or {}))
        return cls(session_maker=session_maker, table_name=table_name)

    @classmethod
    def from_url(
        cls,
        url: Union[str, URL],
        engine_options: Optional[Mapping[str, Any]] = None,
        session_options: Optional[Mapping[str, Any]] = None,
        table_name: str = DEFAULT_TABLE_NAME,
    ) -> Self:
        engine = create_async_engine(url=url, **(engine_options or {}))
        session_maker = async_sessionmaker(bind=engine, **(session_options or {}))
        return cls(session_maker=session_maker, table_name=table_name)

    @property
    def engine(self) -> AsyncEngine:
        return cast(AsyncEngine, self.session_maker.kw["bind"])

    async def get_records(self) -> AsyncIterable[tuple[int, StorageRecord]]:
        statement = select(self.table)
        async with self.session_maker() as session:
            result = await session.execute(statement=statement)
        for mailer_id, data in result.all():
            yield mailer_id, StorageRecord.model_validate_json(json_data=data)

    async def set_record(self, mailer_id: int, record: StorageRecord) -> None:
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

    async def get_record(self, mailer_id: int) -> StorageRecord:
        statement = select(self.table.c.data).where(self.table.c.id == mailer_id)
        async with self.session_maker() as session:
            result = await session.execute(statement=statement)
        data = result.scalar_one()
        return StorageRecord.model_validate_json(json_data=data)

    async def delete_record(self, mailer_id: int) -> None:
        statement = delete(self.table).where(self.table.c.id == mailer_id)
        async with self.session_maker() as session:
            await session.execute(statement=statement)
            await session.commit()

    async def startup(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(self.table.create, checkfirst=True)

    async def shutdown(self) -> None:
        await self.engine.dispose()
