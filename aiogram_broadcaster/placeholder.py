from abc import ABC, abstractmethod
from string import Template
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Container,
    Dict,
    Generator,
    Mapping,
    Optional,
    Set,
    Tuple,
    TypeVar,
    cast,
)

from aiogram.dispatcher.event.handler import CallableObject, CallbackType
from pydantic import BaseModel
from typing_extensions import Self

from .utils.chain import ChainObject


ModelType = TypeVar("ModelType", bound=BaseModel)


class BasePlaceholder(ABC):
    __key__: ClassVar[str]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        if "key" not in kwargs:
            raise ValueError("Missing required argument 'key' when subclassing PlaceholderItem.")
        cls.__key__ = kwargs.pop("key")
        super().__init_subclass__(**kwargs)

    def __repr__(self) -> str:
        return f"PlaceholderItem(key={self.__key__!r})"

    if TYPE_CHECKING:
        __call__: Callable[..., Any]
    else:

        @abstractmethod
        async def __call__(self, **kwargs: Any) -> Any:
            pass


class Placeholder(ChainObject["Placeholder"], sub_name="placeholder"):
    items: Dict[str, Any]

    def __init__(self, name: Optional[str] = None) -> None:
        super().__init__(name=name)

        self.items = {}

    def __setitem__(self, key: str, value: Any) -> None:
        self.add(key=key, value=value)

    def __call__(self, key: str) -> Callable[[CallbackType], CallbackType]:
        def wrapper(callback: CallbackType) -> CallbackType:
            self.add(key=key, value=callback)
            return callback

        return wrapper

    @property
    def chain_keys(self) -> Generator[str, None, None]:
        for placeholder in self.chain_tail:
            yield from placeholder.items

    def add(self, key: str, value: Any) -> Self:
        if key in self.chain_keys:
            raise ValueError(f"Key {key!r} is already exists.")
        if callable(value):
            value = CallableObject(callback=value)
        self.items[key] = value
        return self

    def register(self, *placeholders: BasePlaceholder) -> Self:
        if not placeholders:
            raise ValueError("At least one placeholder must be provided to register.")
        for placeholder in placeholders:
            if not isinstance(placeholder, BasePlaceholder):
                raise TypeError(
                    f"The placeholder must be an instance of "
                    f"PlaceholderItem, not a {type(placeholder).__name__}.",
                )
            self.add(key=placeholder.__key__, value=placeholder.__call__)
        return self

    def attach(self, __mapping: Optional[Mapping[str, Any]] = None, /, **kwargs: Any) -> Self:
        if __mapping:
            kwargs.update(__mapping)
        if not kwargs:
            raise ValueError("At least one keyword must be specified to attaching.")
        for key, value in kwargs.items():
            self.add(key=key, value=value)
        return self

    def _chain_bind(self, entity: "ChainObject[Any]") -> None:
        if collusion := set(self.chain_keys) & set(cast(Placeholder, entity).chain_keys):
            raise ValueError(
                f"The {self.__sub_name__} name={self.name!r} "
                f"already has the keys: {list(collusion)}.",
            )
        super()._chain_bind(entity=entity)


class PlaceholderManager(Placeholder):
    __chain_root__ = True

    TEXT_FIELDS: ClassVar[Set[str]] = {"caption", "text"}

    async def fetch_data(self, __select_keys: Container[str], /, **kwargs: Any) -> Dict[str, Any]:
        return {
            key: await value.call(**kwargs) if isinstance(value, CallableObject) else value
            for placeholder in self.chain_tail
            for key, value in placeholder.items.items()
            if key in __select_keys
        }

    def extract_text_field(self, object: Any) -> Optional[Tuple[str, str]]:  # noqa: A002
        for field in self.TEXT_FIELDS:
            if (value := getattr(object, field, None)) and isinstance(value, str):
                return field, value
        return None

    def extract_keys(self, template: Template) -> Set[str]:
        # fmt: off
        return {
            match.group("named")
            for match in template.pattern.finditer(string=template.template)
        }
        # fmt: on

    async def render(
        self,
        __model: ModelType,
        __exclude_keys: Optional[Set[str]] = None,
        /,
        **kwargs: Any,
    ) -> ModelType:
        self_keys = set(self.chain_keys)
        if not self_keys or __exclude_keys == self_keys:
            return __model
        field = self.extract_text_field(object=__model)
        if not field:
            return __model
        field_name, field_value = field
        template = Template(template=field_value)
        template_keys = self.extract_keys(template=template)
        select_keys = self_keys & template_keys
        if __exclude_keys:
            select_keys -= __exclude_keys
        if not select_keys:
            return __model
        data = await self.fetch_data(select_keys, **kwargs)
        if not data:
            return __model
        rendered_field = {field_name: template.safe_substitute(data)}
        return __model.model_copy(update=rendered_field)
