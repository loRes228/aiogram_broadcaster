from typing import TYPE_CHECKING, Any

from aiogram.methods import TelegramMethod

from aiogram_broadcaster.contents.base import BaseContent


if TYPE_CHECKING:
    from abc import abstractmethod


class LazyContentAdapter(BaseContent, register=False):
    async def as_method(self, **context: Any) -> TelegramMethod[Any]:
        content: BaseContent = await self.call(**context)
        return await content.as_method(**context)

    if TYPE_CHECKING:

        @abstractmethod
        async def __call__(self, *args: Any, **kwargs: Any) -> BaseContent:
            pass
