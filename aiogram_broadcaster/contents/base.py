from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Dict, Type, TypeVar, cast

from aiogram.dispatcher.event.handler import CallableObject
from aiogram.methods import TelegramMethod
from pydantic import (
    BaseModel,
    ConfigDict,
    SerializerFunctionWrapHandler,
    ValidatorFunctionWrapHandler,
    model_serializer,
    model_validator,
)


if TYPE_CHECKING:
    ContentType = TypeVar("ContentType", bound="BaseContent", default="BaseContent")
else:
    ContentType = TypeVar("ContentType", bound="BaseContent")

VALIDATOR_KEY = "__V"


class BaseContent(BaseModel, ABC):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    _validators: ClassVar[Dict[str, Type["BaseContent"]]] = {}
    _callback: ClassVar[CallableObject]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        cls._callback = CallableObject(callback=cls.__call__)
        if kwargs.pop("register", True):
            cls.register()
        super().__init_subclass__(**kwargs)

    if TYPE_CHECKING:
        __call__: Callable[..., Any]
    else:

        @abstractmethod
        async def __call__(self, **kwargs: Any) -> Any:
            pass

    async def as_method(self, **context: Any) -> TelegramMethod[Any]:
        method = await self._callback.call(self, **context)
        return cast(TelegramMethod[Any], method)

    @classmethod
    def is_registered(cls) -> bool:
        return cls.__name__ in cls._validators

    @classmethod
    def register(cls) -> None:
        if cls.is_registered():
            raise RuntimeError(f"The content {cls.__name__!r} is already registered.")
        cls._validators[cls.__name__] = cls

    @model_validator(mode="wrap")
    @classmethod
    def _validate(cls, value: Any, handler: ValidatorFunctionWrapHandler) -> Any:
        if not isinstance(value, dict):
            return handler(value)
        if VALIDATOR_KEY not in value:
            return handler(value)
        validator_name: str = value.pop(VALIDATOR_KEY, None)
        if validator_name not in cls._validators:
            raise ValueError(
                f"Content {validator_name!r} has not been registered, "
                f"you can register using the '{validator_name}.register()' method.",
            )
        return cls._validators[validator_name].model_validate(value)

    @model_serializer(mode="wrap", return_type=Any)
    def _serialize(self, handler: SerializerFunctionWrapHandler) -> Any:
        data = handler(self)
        data[VALIDATOR_KEY] = type(self).__name__
        return data
