from typing import Any

from aiogram.methods import TelegramMethod

from .base import BaseContent


class LazyContent(BaseContent, register=False):
    async def as_method(self, **context: Any) -> TelegramMethod[Any]:
        content = await self._callback.call(**context)
        if not isinstance(content, BaseContent):
            raise TypeError(
                f"The {type(self).__name__!r} expected to return an content of "
                f"type BaseContent, not a {type(content).__name__}.",
            )
        return await content.as_method(**context)
