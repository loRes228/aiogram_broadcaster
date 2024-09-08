from typing import Any, ClassVar

from pydantic import (
    BaseModel,
    SerializerFunctionWrapHandler,
    ValidatorFunctionWrapHandler,
    model_serializer,
    model_validator,
)
from typing_extensions import Self


VALIDATOR_KEY = "__V"


class UnionModel(BaseModel):
    _registry: ClassVar[dict[str, type[BaseModel]]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        if kwargs.pop("register", True):
            cls.register()
        super().__init_subclass__(**kwargs)

    @classmethod
    def register(cls) -> type[Self]:
        cls._registry[cls.__name__] = cls
        return cls

    @classmethod
    def unregister(cls) -> type[Self]:
        cls._registry.pop(cls.__name__, None)
        return cls

    @classmethod
    def is_registered(cls) -> bool:
        return cls.__name__ in cls._registry

    @model_validator(mode="wrap")
    @classmethod
    def _model_validator(cls, value: Any, handler: ValidatorFunctionWrapHandler) -> Any:
        if not isinstance(value, dict):
            return handler(value)
        validator_name = value.pop(VALIDATOR_KEY, None)
        if validator_name is None:
            return handler(value)
        validator = cls._registry.get(validator_name)
        if not validator:
            raise ValueError(f"{validator_name} is not registered.")
        return validator.model_validate(obj=value)

    @model_serializer(mode="wrap", return_type=Any)
    def _model_serializer(self, handler: SerializerFunctionWrapHandler) -> Any:
        data = handler(self)
        data[VALIDATOR_KEY] = type(self).__name__
        return data
