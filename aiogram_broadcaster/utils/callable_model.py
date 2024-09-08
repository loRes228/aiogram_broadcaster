from abc import ABC, abstractmethod
from typing import Any

from aiogram.dispatcher.event.handler import CallableObject
from pydantic import BaseModel


class CallableModel(BaseModel, ABC):
    _callback: CallableObject

    @abstractmethod
    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        pass

    async def call(self, **context: Any) -> Any:
        return await self._callback.call(**context)

    def model_post_init(self, __context: Any) -> None:  # noqa: PYI063
        super().model_post_init(__context)
        self._callback = CallableObject(callback=self.__call__)
