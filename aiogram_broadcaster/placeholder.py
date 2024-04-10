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
    Iterable,
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


class PlaceholderItem(ABC):
    __key__: ClassVar[str]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        if "key" not in kwargs:
            raise ValueError("Missing required argument 'key' when subclassing PlaceholderItem.")
        cls.__key__ = kwargs.pop("key")
        super().__init_subclass__(**kwargs)

    def __repr__(self) -> str:
        return f"PlaceholderItem(key={self.__key__!r})"

    if TYPE_CHECKING:
        __call__: CallbackType
    else:

        @abstractmethod
        async def __call__(self, **kwargs: Any) -> Any:
            pass


class Placeholder(ChainObject, singular_name="placeholder", plural_name="placeholders"):
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

    @property
    def chain_items(self) -> Generator[Tuple[str, Any], None, None]:
        for placeholder in self.chain_tail:
            yield from placeholder.items.items()

    def add(self, key: str, value: Any) -> None:
        if key in self.items:
            raise ValueError(f"Key '{key} 'is already exists.")
        if callable(value):
            value = CallableObject(callback=value)
        self.items[key] = value

    def register(self, *items: PlaceholderItem) -> None:
        if not items:
            raise ValueError("At least one placeholder item must be provided to insertion.")
        for item in items:
            if not isinstance(item, PlaceholderItem):
                raise TypeError(
                    f"The placeholder item must be an instance of "
                    f"PlaceholderItem, not a {type(item).__name__}.",
                )
            self.add(key=item.__key__, value=item.__call__)

    def attach(self, __mapping: Optional[Mapping[str, Any]] = None, /, **kwargs: Any) -> None:
        if __mapping:
            kwargs.update(__mapping)
        self._check_keys_collusion(keys=kwargs)
        self.items.update(kwargs)

    def _set_head(self, entity: "Placeholder") -> None:
        self._check_keys_collusion(keys=entity.chain_keys)
        super()._set_head(entity=entity)

    def _check_keys_collusion(self, keys: Iterable[str]) -> None:
        if keys := set(self.chain_keys) & set(keys):
            raise RuntimeError(f"Collusion between keys: {', '.join(keys)}.")


class PlaceholderWizard(Placeholder):
    __chain_root__ = True

    async def fetch_data(
        self,
        select_keys: Optional[Container[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        if select_keys is None:
            select_keys = set(self.chain_keys)
        return {
            key: await value.call(**kwargs) if isinstance(value, CallableObject) else value
            for key, value in self.chain_items
            if key in select_keys
        }

    def extract_text_field(self, object: Any) -> Optional[Tuple[str, str]]:  # noqa: A002
        for field in ("caption", "text"):
            if value := getattr(object, field, None):
                return field, value
        return None

    def extract_keys(
        self,
        template: Template,
        exclude_keys: Optional[Container[str]] = None,
    ) -> List[str]:
        if exclude_keys is None:
            exclude_keys = set()
        return [
            match.group("named")
            for match in template.pattern.finditer(string=template.template)
            if match.group("named") not in exclude_keys
        ]

    async def render(
        self,
        model: ModelType,
        exclude_keys: Optional[Container[str]] = None,
        **kwargs: Any,
    ) -> ModelType:
        if not tuple(self.chain_keys):
            return model
        field = self.extract_text_field(object=model)
        if not field:
            return model
        field_name, field_value = field
        template = Template(template=field_value)
        keys = self.extract_keys(template=template, exclude_keys=exclude_keys)
        if not keys:
            return model
        data = await self.fetch_data(select_keys=keys, **kwargs)
        if not data:
            return model
        rendered_field = {field_name: template.safe_substitute(data)}
        return model.model_copy(update=rendered_field)
