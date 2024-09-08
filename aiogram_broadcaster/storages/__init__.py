# ruff: noqa: TCH004

__all__ = (
    "BaseStorage",
    "FileStorage",
    "MongoDBStorage",
    "RedisStorage",
    "SQLAlchemyStorage",
)


from typing import TYPE_CHECKING as _TYPE_CHECKING

from aiogram_broadcaster.utils.lazy_importer import lazy_importer as _lazy_importer

from .base import BaseStorage
from .file import FileStorage


if _TYPE_CHECKING:
    from .mongodb import MongoDBStorage
    from .redis import RedisStorage
    from .sqlalchemy import SQLAlchemyStorage


__getattr__ = _lazy_importer(
    package=__name__,
    MongoDBStorage=".mongodb",
    RedisStorage=".redis",
    SQLAlchemyStorage=".sqlalchemy",
)
