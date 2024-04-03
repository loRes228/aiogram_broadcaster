from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Awaitable, Callable, ClassVar, Dict, Type, TypeVar

from aiogram.methods import TelegramMethod
from pydantic import BaseModel, ConfigDict, model_serializer, model_validator
from pydantic_core.core_schema import SerializerFunctionWrapHandler, ValidatorFunctionWrapHandler


VALIDATOR_KEY = "__V"

if TYPE_CHECKING:
    ContentType = TypeVar("ContentType", bound="BaseContent", default="BaseContent")
else:
    ContentType = TypeVar("ContentType", bound="BaseContent")


class BaseContent(BaseModel, ABC):
    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    __validators__: ClassVar[Dict[str, Type["BaseContent"]]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        cls.__validators__[cls.__name__] = cls
        super().__init_subclass__(**kwargs)

    if TYPE_CHECKING:
        as_method: ClassVar[Callable[..., Awaitable[TelegramMethod[Any]]]]
    else:

        @abstractmethod
        async def as_method(self, **kwargs: Any) -> TelegramMethod[Any]:
            pass

    @model_validator(mode="wrap")
    @classmethod
    def _validate(
        cls,
        value: Any,
        handler: ValidatorFunctionWrapHandler,
    ) -> Any:
        if not isinstance(value, dict):
            return handler(value)
        validator: str = value.pop(VALIDATOR_KEY, None)
        if not validator:
            return handler(value)
        if validator not in cls.__validators__:
            raise RuntimeError(f"Content '{validator}' was not found.")
        return cls.__validators__[validator].model_validate(value)

    @model_serializer(mode="wrap", return_type=Any)
    def _serialize(self, handler: SerializerFunctionWrapHandler) -> Any:
        data = handler(self)
        data[VALIDATOR_KEY] = type(self).__name__
        return data
