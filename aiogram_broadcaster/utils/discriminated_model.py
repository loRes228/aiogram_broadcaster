from collections.abc import Generator
from typing import Any

from pydantic import (
    BaseModel,
    SerializerFunctionWrapHandler,
    ValidatorFunctionWrapHandler,
    model_serializer,
    model_validator,
)


VALIDATOR_KEY = "__V"


class DiscriminatedModel(BaseModel):
    @classmethod
    def _get_subclasses(cls) -> Generator[type[BaseModel], None, None]:
        yield cls
        for subclass in cls.__subclasses__():
            yield from subclass._get_subclasses()  # noqa: SLF001

    @classmethod
    def _get_validator(cls, name: str) -> type[BaseModel]:
        for subclass in cls._get_subclasses():
            if subclass.__name__ == name:
                return subclass
        raise ValueError(f"The validator '{name}' was not found.")

    @model_validator(mode="wrap")
    @classmethod
    def _model_validator(cls, value: Any, handler: ValidatorFunctionWrapHandler) -> Any:
        if not isinstance(value, dict):
            return handler(value)
        validator_name = value.pop(VALIDATOR_KEY, None)
        if validator_name is None:
            return handler(value)
        validator = cls._get_validator(name=validator_name)
        return validator.model_validate(obj=value)

    @model_serializer(mode="wrap", return_type=Any)
    def _model_serializer(self, handler: SerializerFunctionWrapHandler) -> Any:
        data = handler(self)
        data[VALIDATOR_KEY] = type(self).__name__
        return data
