from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, Union

from aiogram.dispatcher.event.handler import CallableObject


RenderResult = Optional[tuple[dict[str, Any], Callable[[Any], str]]]


class BasePlaceholderItem(ABC):
    _value: Union[CallableObject, Any]

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

    async def render(self, source: str, /, **context: Any) -> str:
        render_result: RenderResult = self._render(source=source)
        if not render_result:
            return source
        render_data, render_method = render_result
        context.update(render_data, item=self)
        value: Any = await self._get_value(**context)
        return render_method(value)

    async def _get_value(self, **context: Any) -> Any:
        if isinstance(self._value, CallableObject):
            return await self._value.call(**context)
        return self._value

    @abstractmethod
    def _render(self, source: str) -> RenderResult:
        pass
