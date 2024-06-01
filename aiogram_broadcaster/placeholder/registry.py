from typing import Any, Callable, Generator, Iterator, Mapping, Optional, Set, Tuple

from aiogram.dispatcher.event.handler import CallbackType
from typing_extensions import Self

from aiogram_broadcaster.utils.chain import Chain

from .item import PlaceholderItem
from .placeholder import Placeholder


class PlaceholderRegistry(Chain["PlaceholderRegistry"], sub_name="placeholder"):
    placeholders: Set[Placeholder]

    def __init__(self, name: Optional[str] = None) -> None:
        super().__init__(name=name)

        self.placeholders = set()

    def __setitem__(self, key: str, value: Any) -> None:
        self.placeholders.add(Placeholder(key=key, value=value))

    def __getitem__(self, item: str) -> Any:
        return dict(self.chain_items)[item]

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        return iter(self.chain_items)

    def __contains__(self, item: str) -> bool:
        return item in self.chain_keys

    def __call__(self, key: str) -> Callable[[CallbackType], CallbackType]:
        def wrapper(callback: CallbackType) -> CallbackType:
            self[key] = callback
            return callback

        return wrapper

    @property
    def items(self) -> Tuple[Tuple[str, Any], ...]:
        return tuple((placeholder.key, placeholder.value) for placeholder in self.placeholders)

    @property
    def keys(self) -> Set[str]:
        return {placeholder.key for placeholder in self.placeholders}

    @property
    def chain_placeholders(self) -> Generator[Placeholder, None, None]:
        for registry in self.chain_tail:
            yield from registry.placeholders

    @property
    def chain_items(self) -> Generator[Tuple[str, Any], None, None]:
        for registry in self.chain_tail:
            yield from registry.items

    @property
    def chain_keys(self) -> Generator[str, None, None]:
        for registry in self.chain_tail:
            yield from registry.keys

    def register(self, *items: PlaceholderItem) -> Self:
        if not items:
            raise ValueError("At least one placeholder item must be provided to register.")
        self.placeholders.update(item.as_placeholder() for item in items)
        return self

    def add(self, __mapping: Optional[Mapping[str, Any]] = None, /, **kwargs: Any) -> Self:
        if __mapping:
            kwargs.update(__mapping)
        if not kwargs:
            raise ValueError("At least one argument must be provided.")
        self.placeholders.update(
            Placeholder(key=key, value=value) for key, value in kwargs.items()
        )
        return self

    def _chain_bind(self, entity: "PlaceholderRegistry") -> None:
        for self_registry in self.chain_tail:
            for entity_registry in entity.chain_tail:
                if collision_keys := self_registry.keys & entity_registry.keys:
                    raise RuntimeError(
                        f"Collision keys={list(collision_keys)!r} "
                        f"between PlaceholderRegistry(name={entity_registry.name!r}) "
                        f"and PlaceholderRegistry(name={self_registry.name!r}).",
                    )
        super()._chain_bind(entity=entity)
