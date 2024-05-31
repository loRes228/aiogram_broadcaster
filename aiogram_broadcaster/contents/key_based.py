from typing import TYPE_CHECKING, Any, Dict, Optional

from aiogram.methods import TelegramMethod
from pydantic import SerializeAsAny

from .base import BaseContent


class KeyBasedContent(BaseContent, register=False):
    default: Optional[SerializeAsAny[BaseContent]] = None
    __pydantic_extra__: Dict[str, SerializeAsAny[BaseContent]]

    def __getitem__(self, item: str) -> BaseContent:
        if self.default:
            return self.__pydantic_extra__.get(item, self.default)
        return self.__pydantic_extra__[item]

    def __contains__(self, item: str) -> bool:
        return item in self.__pydantic_extra__

    async def as_method(self, **context: Any) -> TelegramMethod[Any]:
        key = await self._callback.call(**context)
        return await self[key].as_method(**context)

    def model_post_init(self, __context: Any) -> None:
        if not self.default and not self.__pydantic_extra__:
            raise ValueError("At least one content must be specified.")
        super().model_post_init(__context)

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            default: Optional[BaseContent] = ...,
            **contents: BaseContent,
        ) -> None: ...
