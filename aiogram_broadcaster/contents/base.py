from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Awaitable, Callable, ClassVar, Dict, Type

from aiogram.methods.base import TelegramMethod
from pydantic import (
    BaseModel,
    ConfigDict,
    SerializerFunctionWrapHandler,
    model_serializer,
    model_validator,
)
from pydantic.functional_validators import ModelWrapValidatorHandler


VALIDATOR_KEY = "__validator"


class BaseContent(BaseModel, ABC):
    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    __validators__: ClassVar[Dict[str, Type["BaseContent"]]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls.__validators__[cls.__name__] = cls

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
        __value: Any,
        __handler: ModelWrapValidatorHandler["BaseContent"],
    ) -> "BaseContent":
        if not isinstance(__value, dict):
            return __handler(__value)
        if validator := __value.pop(VALIDATOR_KEY, None):
            return cls.__validators__[validator].model_validate(__value)
        return __handler(__value)

    @model_serializer(mode="wrap", return_type=Any)
    def _serialize(self, handler: SerializerFunctionWrapHandler) -> Any:
        data = handler(self)
        data[VALIDATOR_KEY] = type(self).__name__
        return data
