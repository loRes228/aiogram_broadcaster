from typing import Any

from aiogram.dispatcher.event.handler import CallableObject


class Placeholder:
    key: str
    _value: Any

    def __init__(self, key: str, value: Any) -> None:
        self.key = key
        if callable(value):
            value = CallableObject(callback=value)
        self._value = value

    def __hash__(self) -> int:
        return hash(self.key)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Placeholder):
            return False
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
