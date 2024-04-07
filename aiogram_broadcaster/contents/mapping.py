from typing import TYPE_CHECKING, Any, Dict

from aiogram.methods import TelegramMethod
from pydantic import ConfigDict, SerializeAsAny

from .base import BaseContent


class MappingContent(BaseContent):
    model_config = ConfigDict(extra="allow")

    __pydantic_extra__: Dict[str, SerializeAsAny[BaseContent]]

    async def as_method(self, **kwargs: Any) -> TelegramMethod[Any]:
        key = await self._callback.call(self, **kwargs)
        content = self.resolve_content(key=key)
        return await content.as_method(**kwargs)

    def resolve_content(self, key: Any) -> BaseContent:
        return self.__pydantic_extra__[key]

    if TYPE_CHECKING:

        def __init__(self, **contents: BaseContent) -> None: ...


class DefaultMappingContent(MappingContent):
    default: SerializeAsAny[BaseContent]

    def resolve_content(self, key: Any) -> BaseContent:
        return self.__pydantic_extra__.get(key, self.default)

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            default: BaseContent,
            **contents: BaseContent,
        ) -> None: ...
