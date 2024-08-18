from typing import TYPE_CHECKING, Any, TypeVar

from aiogram.methods import TelegramMethod
from pydantic import ConfigDict
from pydantic_discriminated_model import DiscriminatedModel

from aiogram_broadcaster.utils.callable_model import CallableModel


if TYPE_CHECKING:
    ContentType = TypeVar("ContentType", bound="BaseContent", default="BaseContent")
else:
    ContentType = TypeVar("ContentType", bound="BaseContent")


class BaseContent(DiscriminatedModel, CallableModel, register=False):
    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    async def as_method(self, **context: Any) -> TelegramMethod[Any]:
        method: TelegramMethod[Any] = await self.call(**context)
        return method
