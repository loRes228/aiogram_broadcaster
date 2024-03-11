from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, Optional, cast

from aiogram.dispatcher.event.handler import CallableObject
from aiogram.methods.base import TelegramMethod
from pydantic import ConfigDict, SerializeAsAny

from .contents import BaseContent


class BaseLanguageGetter(ABC):  # noqa: B024
    def __init__(self) -> None:
        self.callback = CallableObject(callback=self.__call__)

    async def get_language(self, **kwargs: Any) -> Optional[str]:
        language = await self.callback.call(**kwargs)
        return cast(Optional[str], language)

    if TYPE_CHECKING:
        __call__: Callable[..., Awaitable[Optional[str]]]
    else:

        @abstractmethod
        async def __call__(self, **kwargs: Any) -> Optional[str]:
            pass


class L10nContentAdapter(BaseContent):
    model_config = ConfigDict(extra="allow")
    default: SerializeAsAny[BaseContent]
    __pydantic_extra__: Dict[str, SerializeAsAny[BaseContent]]

    async def as_method(
        self,
        language_getter: BaseLanguageGetter,
        **kwargs: Any,
    ) -> TelegramMethod[Any]:
        language = await language_getter.get_language(**kwargs)
        content = self.resolve_content(language=language)
        return await content.as_method(**kwargs)

    def resolve_content(self, language: Optional[str]) -> BaseContent:
        if language is None or not self.model_extra:
            return self.default
        content = self.model_extra.get(language, self.default)
        return cast(BaseContent, content)

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            default: BaseContent,
            **contents: BaseContent,
        ) -> None: ...
