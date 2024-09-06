from asyncio import Event
from typing import TYPE_CHECKING, Any

from aiogram_broadcaster.utils.callable_model import CallableModel
from aiogram_broadcaster.utils.sleep import sleep
from aiogram_broadcaster.utils.union_model import UnionModel


if TYPE_CHECKING:
    from abc import abstractmethod


class BaseInterval(UnionModel, CallableModel, register=False):
    async def sleep(self, event: Event, /, **context: Any) -> bool:
        if event.is_set():
            return False
        delay = await self.call(**context)
        if not delay:
            return True
        return await sleep(event=event, delay=delay)

    if TYPE_CHECKING:

        @abstractmethod
        async def __call__(self, *args: Any, **kwargs: Any) -> float:
            pass
