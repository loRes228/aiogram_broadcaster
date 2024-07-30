# ruff: noqa: TCH004

__all__ = (
    "BasePlaceholderItem",
    "JinjaPlaceholderItem",
    "RegexpPlaceholderItem",
    "StringPlaceholderItem",
)


from typing import TYPE_CHECKING as _TYPE_CHECKING

from aiogram_broadcaster.utils.lazy_importer import lazy_importer as _lazy_importer

from .base import BasePlaceholderItem
from .regexp import RegexpPlaceholderItem
from .string import StringPlaceholderItem


if _TYPE_CHECKING:
    from .jinja import JinjaPlaceholderItem


__getattr__ = _lazy_importer(
    package=__name__,
    JinjaPlaceholderItem=".jinja",
)
