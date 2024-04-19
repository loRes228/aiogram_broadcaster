# ruff: noqa: TCH004, PLC0415

from typing import TYPE_CHECKING as _TYPE_CHECKING


if _TYPE_CHECKING:
    from .base import BaseMailerStorage
    from .file import FileMailerStorage
    from .redis import RedisMailerStorage
    from .sqlalchemy import SQLAlchemyMailerStorage

__all__ = (
    "BaseMailerStorage",
    "FileMailerStorage",
    "RedisMailerStorage",
    "SQLAlchemyMailerStorage",
)


def __getattr__(name: str) -> type:
    if name == "BaseMailerStorage":
        from .base import BaseMailerStorage

        return BaseMailerStorage

    if name == "FileMailerStorage":
        from .file import FileMailerStorage

        return FileMailerStorage

    if name == "RedisMailerStorage":
        from .redis import RedisMailerStorage

        return RedisMailerStorage

    if name == "SQLAlchemyMailerStorage":
        from .sqlalchemy import SQLAlchemyMailerStorage

        return SQLAlchemyMailerStorage

    raise AttributeError
