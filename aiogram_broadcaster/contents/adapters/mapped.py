from typing import TYPE_CHECKING, Any, Optional

from aiogram.methods import TelegramMethod
from pydantic import SerializeAsAny

from aiogram_broadcaster.contents.base import BaseContent


if TYPE_CHECKING:
    from abc import abstractmethod


class MappedContentAdapter(BaseContent, register=False):
    default: Optional[SerializeAsAny[BaseContent]] = None
    __pydantic_extra__: dict[str, SerializeAsAny[BaseContent]]

    def __getitem__(self, item: str) -> BaseContent:
        if self.default:
            return self.__pydantic_extra__.get(item, self.default)
        try:
            return self.__pydantic_extra__[item]
        except KeyError as error:
            raise KeyError(
                f"The '{type(self).__name__}' cannot find content by the '{item}' key.",
            ) from error

    def __contains__(self, item: str) -> bool:
        return item in self.__pydantic_extra__

    async def as_method(self, **context: Any) -> TelegramMethod[Any]:
        key = await self.call(**context)
        content = self[key]
        return await content.as_method(**context)

    def model_post_init(self, __context: Any) -> None:  # noqa: PYI063
        super().model_post_init(__context)
        if not self.default and not self.model_extra:
            raise ValueError("At least one content must be provided.")

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            default: Optional[BaseContent] = ...,
            **contents: BaseContent,
        ) -> None: ...

        @abstractmethod
        async def __call__(self, *args: Any, **kwargs: Any) -> Optional[str]:
            pass
