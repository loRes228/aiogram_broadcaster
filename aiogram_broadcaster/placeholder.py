from string import Template
from types import FunctionType
from typing import (
    Any,
    Callable,
    Container,
    Dict,
    Generator,
    List,
    Mapping,
    Optional,
    Tuple,
    TypeVar,
)

from aiogram.dispatcher.event.handler import CallableObject, CallbackType
from pydantic import BaseModel

from .utils.chain import ChainObject


ModelType = TypeVar("ModelType", bound=BaseModel)


class Placeholder(ChainObject):
    name: str
    values: Dict[str, Any]

    def __init__(self, name: Optional[str] = None) -> None:
        super().__init__(entity=Placeholder, sub_name="placeholder")

        self.name = name or hex(id(self))
        self.values = {}

    def __setitem__(self, key: str, value: Any) -> None:
        self.add(key=key, value=value)

    def __call__(self, key: str) -> Callable[[CallbackType], CallbackType]:
        def wrapper(callback: CallbackType) -> CallbackType:
            self.add(key=key, value=callback)
            return callback

        return wrapper

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.name!r}, keys={list(self.chain_keys)})"

    @property
    def chain_keys(self) -> Generator[str, None, None]:
        for placeholder in self.chain_tail:
            yield from placeholder.values

    @property
    def chain_items(self) -> Generator[Tuple[str, Any], None, None]:
        for placeholder in self.chain_tail:
            yield from placeholder.values.items()

    def add(self, key: str, value: Any) -> None:
        if key in self.values:
            raise KeyError(f"Key {key!r} is already exists.")
        if isinstance(value, FunctionType):
            value = CallableObject(callback=value)
        self.values[key] = value

    def attach(self, __mapping: Optional[Mapping[str, Any]] = None, /, **kwargs: Any) -> None:
        if __mapping:
            kwargs.update(__mapping)
        if keys_collusion := set(self.chain_keys) & set(kwargs):
            raise RuntimeError(f"Collusion between keys was detected: {keys_collusion}.")
        self.values.update(kwargs)

    def _set_parent_entity(self, entity: "Placeholder") -> None:
        if keys_collusion := set(self.chain_keys) & set(entity.chain_keys):
            raise RuntimeError(f"Collusion between keys was detected: {keys_collusion}.")
        super()._set_parent_entity(entity=entity)


class PlaceholderWizard(Placeholder):
    __chain_root__ = True

    async def fetch_data(
        self,
        select: Optional[Container[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        if select is None:
            select = set(self.chain_keys)
        return {
            key: await value.call(**kwargs) if isinstance(value, CallableObject) else value
            for key, value in self.chain_items
            if key in select
        }

    def extract_text_field(self, object: Any) -> Optional[Tuple[str, str]]:  # noqa: A002
        for field in ("caption", "text"):
            if value := getattr(object, field, None):
                return field, value
        return None

    def extract_placeholders(
        self,
        template: Template,
        exclude: Optional[Container[str]] = None,
    ) -> List[str]:
        if exclude is None:
            exclude = set()
        return [
            match.group("named")
            for match in template.pattern.finditer(string=template.template)
            if match.group("named") not in exclude
        ]

    async def render(
        self,
        model: ModelType,
        exclude: Optional[Container[str]] = None,
        **kwargs: Any,
    ) -> ModelType:
        if not tuple(self.chain_keys):
            return model
        field = self.extract_text_field(object=model)
        if not field:
            return model
        field_name, field_value = field
        template = Template(template=field_value)
        placeholders = self.extract_placeholders(template=template, exclude=exclude)
        if not placeholders:
            return model
        data = await self.fetch_data(select=placeholders, **kwargs)
        if not data:
            return model
        rendered_field = {field_name: template.safe_substitute(data)}
        return model.model_copy(update=rendered_field)
