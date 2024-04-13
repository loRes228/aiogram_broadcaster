# ruff: noqa: PLC0415,TCH004

from typing import TYPE_CHECKING as _TYPE_CHECKING


if _TYPE_CHECKING:
    from .base import BaseBCRStorage
    from .file import FileBCRStorage
    from .redis import RedisBCRStorage

__all__ = (
    "BaseBCRStorage",
    "FileBCRStorage",
    "RedisBCRStorage",
)


def __getattr__(name: str) -> type:
    if name == "BaseBCRStorage":
        from .base import BaseBCRStorage

        return BaseBCRStorage

    if name == "FileBCRStorage":
        from .file import FileBCRStorage

        return FileBCRStorage

    if name == "RedisBCRStorage":
        from .redis import RedisBCRStorage

        return RedisBCRStorage

    raise AttributeError
