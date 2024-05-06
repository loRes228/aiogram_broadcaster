from typing import TYPE_CHECKING, Any, Dict, Optional

from aiogram.methods import TelegramMethod
from pydantic import ConfigDict, SerializeAsAny

from .base import BaseContent


class KeyBasedContent(BaseContent, register=False):
    model_config = ConfigDict(extra="allow")

    default: Optional[SerializeAsAny[BaseContent]] = None
    __pydantic_extra__: Dict[str, SerializeAsAny[BaseContent]]

    def __getitem__(self, item: str) -> BaseContent:
        return self.__pydantic_extra__[item]

    def __contains__(self, item: str) -> bool:
        return item in self.__pydantic_extra__

    def model_post_init(self, __context: Any) -> None:
        if not self.default and not self.__pydantic_extra__:
            raise ValueError("At least one content must be specified.")

    async def as_method(self, **context: Any) -> TelegramMethod[Any]:
        key = await self._callback.call(self, **context)
        content = self.resolve_content(key=key)
        return await content.as_method(**context)

    def resolve_content(self, key: Any) -> BaseContent:
        if self.default:
            return self.__pydantic_extra__.get(key, self.default)
        return self.__pydantic_extra__[key]

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            default: Optional[BaseContent] = ...,
            **contents: BaseContent,
        ) -> None: ...
