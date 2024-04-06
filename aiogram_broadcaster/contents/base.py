from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Awaitable, Callable, ClassVar, Dict, Type, TypeVar

from aiogram.methods import TelegramMethod
from pydantic import (
    BaseModel,
    ConfigDict,
    SerializerFunctionWrapHandler,
    ValidatorFunctionWrapHandler,
    model_serializer,
    model_validator,
)


VALIDATOR_KEY = "__V"

if TYPE_CHECKING:
    ContentType = TypeVar("ContentType", bound="BaseContent", default="BaseContent")
else:
    ContentType = TypeVar("ContentType", bound="BaseContent")


class BaseContent(BaseModel, ABC):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    __validators__: ClassVar[Dict[str, Type["BaseContent"]]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        if kwargs.pop("register", True):
            cls.register()
        super().__init_subclass__(**kwargs)

    @classmethod
    def is_registered(cls) -> bool:
        return cls.__name__ in cls.__validators__

    @classmethod
    def register(cls) -> None:
        if cls.is_registered():
            raise RuntimeError(f"The content '{cls.__name__}' is already registered.")
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
        value: Any,
        handler: ValidatorFunctionWrapHandler,
    ) -> Any:
        if not isinstance(value, dict):
            return handler(value)
        validator_name: str = value.pop(VALIDATOR_KEY, None)
        if not validator_name:
            return handler(value)
        if validator_name not in cls.__validators__:
            raise RuntimeError(
                f"Content '{validator_name}' has not been registered, "
                f"you can register using the '{validator_name}.register()' method.",
            )
        return cls.__validators__[validator_name].model_validate(value)

    @model_serializer(mode="wrap", return_type=Any)
    def _serialize(self, handler: SerializerFunctionWrapHandler) -> Any:
        data = handler(self)
        data[VALIDATOR_KEY] = type(self).__name__
        return data
