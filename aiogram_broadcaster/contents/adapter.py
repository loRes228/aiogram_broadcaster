from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, Optional, cast

from aiogram.dispatcher.event.handler import CallableObject
from aiogram.methods import TelegramMethod
from pydantic import ConfigDict, PrivateAttr, SerializeAsAny

from .base import BaseContent


class ContentAdapter(BaseContent):
    model_config = ConfigDict(extra="allow")

    default: SerializeAsAny[BaseContent]
    __pydantic_extra__: Dict[str, SerializeAsAny[BaseContent]]
    _callback: CallableObject = PrivateAttr()

    if TYPE_CHECKING:
        __call__: Callable[..., Awaitable[Optional[str]]]
    else:

        @abstractmethod
        async def __call__(self, **kwargs: Any) -> Optional[str]:
            pass

    def model_post_init(self, __context: Any) -> None:
        self._callback = CallableObject(callback=self.__call__)

    async def as_method(self, **kwargs: Any) -> TelegramMethod[Any]:
        ident = await self._callback.call(**kwargs)
        content = self.resolve_content(ident=ident)
        return await content.as_method(**kwargs)

    def resolve_content(self, ident: Optional[str]) -> BaseContent:
        if ident is None or not self.model_extra:
            return self.default
        content = self.model_extra.get(ident, self.default)
        return cast(BaseContent, content)

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            default: BaseContent,
            **contents: BaseContent,
        ) -> None: ...
