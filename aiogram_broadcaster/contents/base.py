from typing import TYPE_CHECKING, Any, TypeVar

from aiogram.methods import TelegramMethod
from pydantic import ConfigDict

from aiogram_broadcaster.utils.callable_model import CallableModel
from aiogram_broadcaster.utils.union_model import UnionModel


if TYPE_CHECKING:
    ContentType = TypeVar("ContentType", bound="BaseContent", default="BaseContent")
else:
    ContentType = TypeVar("ContentType", bound="BaseContent")


class BaseContent(UnionModel, CallableModel, register=False):
    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    async def as_method(self, **context: Any) -> TelegramMethod[Any]:
        method: TelegramMethod[Any] = await self.call(**context)
        return method
