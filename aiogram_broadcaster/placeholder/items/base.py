from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable

from aiogram.dispatcher.event.handler import CallableObject
from typing_extensions import Self


if TYPE_CHECKING:
    from aiogram_broadcaster.placeholder.placeholder import Placeholder


class BasePlaceholderItem:
    def __init__(self, value: Any) -> None:
        self._value = CallableObject(callback=value) if callable(value) else value

    def __hash__(self) -> int:
        return hash((type(self), repr(vars(self))))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BasePlaceholderItem):
            return NotImplemented
        return hash(self) == hash(other)

    @property
    def value(self) -> Any:
        if isinstance(self._value, CallableObject):
            return self._value.callback
        return self._value

    async def get_value(self, **context: Any) -> Any:
        if isinstance(self._value, CallableObject):
            return await self._value.call(**context)
        return self._value


class BasePlaceholderDecorator(ABC):
    def __init__(self, placeholder: "Placeholder") -> None:
        self._placeholder = placeholder

    def __call__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def wrapper(callback: Callable[..., Any]) -> Callable[..., Any]:
            self.register(callback, *args, **kwargs)
            return callback

        return wrapper

    def register(self, *args: Any, **kwargs: Any) -> Self:
        item = self.__item_class__(*args, **kwargs)
        self._placeholder.register(item)
        return self

    @property
    @abstractmethod
    def __item_class__(self) -> type[BasePlaceholderItem]:
        pass


class BasePlaceholderEngine(ABC):
    @abstractmethod
    async def render(self, source: str, *items: Any, **context: Any) -> str:
        pass
