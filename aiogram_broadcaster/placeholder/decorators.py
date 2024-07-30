# ruff: noqa: PLC0415

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Union

from typing_extensions import Self

from aiogram_broadcaster.utils.common_types import CallbackType, WrapperType

from .items.base import BasePlaceholderItem


if TYPE_CHECKING:
    from re import Pattern, RegexFlag

    from .items.regexp import RegexMode
    from .placeholder import Placeholder


class BasePlaceholderDecorator(ABC):
    _placeholder: "Placeholder"

    def __init__(self, placeholder: "Placeholder") -> None:
        self._placeholder = placeholder

    def __call__(self, *args: Any, **kwargs: Any) -> WrapperType:
        def wrapper(callback: CallbackType) -> CallbackType:
            self.register(callback, *args, **kwargs)
            return callback

        return wrapper

    def register(self, *args: Any, **kwargs: Any) -> Self:
        item: BasePlaceholderItem = self._item_class(*args, **kwargs)
        self._placeholder.register(item)
        return self

    @property
    @abstractmethod
    def _item_class(self) -> type[BasePlaceholderItem]:
        pass


class JinjaPlaceholderDecorator(BasePlaceholderDecorator):
    if TYPE_CHECKING:

        def __call__(
            self,
            name: str,
            **template_options: Any,
        ) -> WrapperType: ...

        def register(
            self,
            value: Any,
            name: str,
            **template_options: Any,
        ) -> Self: ...

    @property
    def _item_class(self) -> type[BasePlaceholderItem]:
        from .items.jinja import JinjaPlaceholderItem

        return JinjaPlaceholderItem


class RegexpPlaceholderDecorator(BasePlaceholderDecorator):
    if TYPE_CHECKING:

        def __call__(
            self,
            pattern: Union[str, Pattern[str]],
            flags: Union[int, RegexFlag] = ...,
            mode: RegexMode = ...,
        ) -> WrapperType: ...

        def register(
            self,
            value: Any,
            pattern: Union[str, Pattern[str]],
            flags: Union[int, RegexFlag] = ...,
            mode: RegexMode = ...,
        ) -> Self: ...

    @property
    def _item_class(self) -> type[BasePlaceholderItem]:
        from .items.regexp import RegexpPlaceholderItem

        return RegexpPlaceholderItem


class StringPlaceholderDecorator(BasePlaceholderDecorator):
    if TYPE_CHECKING:

        def __call__(
            self,
            name: str,
        ) -> WrapperType: ...

        def register(
            self,
            value: Any,
            name: str,
        ) -> Self: ...

    @property
    def _item_class(self) -> type[BasePlaceholderItem]:
        from .items.string import StringPlaceholderItem

        return StringPlaceholderItem
