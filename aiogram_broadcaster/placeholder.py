from abc import ABC, abstractmethod
from string import Template
from types import MappingProxyType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Container,
    Dict,
    Generator,
    Iterator,
    Mapping,
    Optional,
    Set,
    Tuple,
    TypeVar,
)

from aiogram.dispatcher.event.handler import CallableObject, CallbackType
from pydantic import BaseModel
from typing_extensions import Self

from .utils.chain import ChainObject
from .utils.interrupt import suppress_interrupt


ModelType = TypeVar("ModelType", bound=BaseModel)


class PlaceholderItem(ABC):
    key: ClassVar[str]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        if "key" not in kwargs:
            raise ValueError("Missing required argument 'key' when subclassing PlaceholderItem.")
        cls.key = kwargs.pop("key")
        super().__init_subclass__(**kwargs)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(key={self.key!r})"

    if TYPE_CHECKING:
        __call__: Callable[..., Any]
    else:

        @abstractmethod
        async def __call__(self, **kwargs: Any) -> Any:
            pass


class PlaceholderRouter(ChainObject["PlaceholderRouter"], sub_name="placeholder"):
    _items: Dict[str, Any]

    def __init__(self, name: Optional[str] = None) -> None:
        super().__init__(name=name)

        self._items = {}

    def __setitem__(self, key: str, value: Any) -> None:
        self.add(key=key, value=value)

    def __getitem__(self, item: str) -> Any:
        return dict(self.chain_items)[item]

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        return iter(self.chain_items)

    def __contains__(self, item: str) -> bool:
        return item in self.chain_keys

    def __call__(self, key: str) -> Callable[[CallbackType], CallbackType]:
        def wrapper(callback: CallbackType) -> CallbackType:
            self.add(key=key, value=callback)
            return callback

        return wrapper

    @property
    def items(self) -> Mapping[str, Any]:
        return MappingProxyType(mapping=self._items)

    @property
    def chain_keys(self) -> Generator[str, None, None]:
        for placeholder in self.chain_tail:
            yield from placeholder.items

    @property
    def chain_items(self) -> Generator[Tuple[str, Any], None, None]:
        for placeholder in self.chain_tail:
            yield from placeholder.items.items()

    def add(self, key: str, value: Any) -> Self:
        if key in self.chain_keys:
            raise ValueError(f"Key {key!r} is already exists.")
        if callable(value):
            value = CallableObject(callback=value)
        self._items[key] = value
        return self

    def register(self, *items: PlaceholderItem) -> Self:
        if not items:
            raise ValueError("At least one placeholder item must be provided to register.")
        for item in items:
            if not isinstance(item, PlaceholderItem):
                raise TypeError(
                    f"The placeholder item must be an instance of "
                    f"PlaceholderItem, not a {type(item).__name__}.",
                )
            self.add(key=item.key, value=item.__call__)
        return self

    def attach(self, __mapping: Optional[Mapping[str, Any]] = None, /, **kwargs: Any) -> Self:
        if __mapping:
            kwargs.update(__mapping)
        if not kwargs:
            raise ValueError("At least one keyword argument must be specified to attaching.")
        for key, value in kwargs.items():
            self.add(key=key, value=value)
        return self

    def _chain_bind(self, entity: "PlaceholderRouter") -> None:
        if collusion := set(self.chain_keys) & set(entity.chain_keys):
            raise ValueError(
                f"The {self.__sub_name} name={self.name!r} "
                f"already has the keys: {list(collusion)}.",
            )
        super()._chain_bind(entity=entity)


class PlaceholderManager(PlaceholderRouter):
    __chain_root__ = True

    TEXT_FIELDS: ClassVar[Set[str]] = {"caption", "text"}

    async def fetch_data(self, __select_keys: Container[str], /, **context: Any) -> Dict[str, Any]:
        data = {}
        for key, value in self.chain_items:
            if key not in __select_keys:
                continue
            with suppress_interrupt():
                data[key] = (
                    await value.call(**context) if isinstance(value, CallableObject) else value
                )
        return data

    def extract_text_field(self, model: BaseModel) -> Optional[Tuple[str, str]]:
        if not self.TEXT_FIELDS & model.model_fields_set:
            return None
        mapped_model = dict(model)
        for field_name in self.TEXT_FIELDS:
            if (field_value := mapped_model.get(field_name)) and isinstance(field_value, str):
                return field_name, field_value
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
        **context: Any,
    ) -> ModelType:
        self_keys = set(self.chain_keys)
        if not self_keys or __exclude_keys == self_keys:
            return __model
        field = self.extract_text_field(model=__model)
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
        data = await self.fetch_data(select_keys, **context)
        if not data:
            return __model
        rendered_field = {field_name: template.safe_substitute(data)}
        return __model.model_copy(update=rendered_field)
