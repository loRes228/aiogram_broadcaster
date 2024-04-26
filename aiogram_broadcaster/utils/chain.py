from typing import Any, ClassVar, Generator, Generic, List, Optional, TypeVar, overload
from unittest.mock import sentinel


EntityType = TypeVar("EntityType", bound="ChainObject[Any]")

UNSET_ENTITY = sentinel.UNSET_ENTITY


class ChainObject(Generic[EntityType]):
    __chain_root__: ClassVar[bool] = False
    __entity: EntityType = UNSET_ENTITY
    __sub_name: ClassVar[str]
    name: str
    head: Optional[EntityType]
    tail: List[EntityType]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        if cls.__entity is UNSET_ENTITY:
            cls.__entity = cls
            cls.__sub_name = kwargs.pop("sub_name", cls.__name__.lower())
        super().__init_subclass__(**kwargs)

    def __init__(self, name: Optional[str] = None) -> None:
        self.name = hex(id(self)) if name is None else name
        self.head = None
        self.tail = []

    def __repr__(self) -> str:
        fields = [f"name={self.name!r}"]
        if self.tail:
            fields.append(f"nested={list(self.tail)!r}")
        fields_sting = ", ".join(fields)
        return f"{type(self).__name__}({fields_sting})"

    def __str__(self) -> str:
        fields = [f"name={self.name!r}"]
        if self.head:
            fields.append(f"parent={self.head!s}")
        fields_sting = ", ".join(fields)
        return f"{type(self).__name__}({fields_sting})"

    @property
    def chain_head(self: EntityType) -> Generator[EntityType, None, None]:
        entity: Optional[EntityType] = self
        while entity:
            yield entity
            entity = entity.head

    @property
    def chain_tail(self: EntityType) -> Generator[EntityType, None, None]:
        yield self
        for entity in self.tail:
            yield from entity.chain_tail

    @overload
    def include(self: EntityType, entity: EntityType, /) -> EntityType: ...  # type: ignore[overload-overlap]

    @overload
    def include(self: EntityType, *entities: EntityType) -> None: ...

    def include(self: EntityType, *entities: EntityType) -> Optional[EntityType]:
        if not entities:
            raise ValueError(
                f"At least one {self.__sub_name} must be provided to include.",
            )
        for entity in entities:
            if not isinstance(entity, self.__entity):
                raise TypeError(
                    f"The {self.__sub_name} must be an instance of "
                    f"{self.__entity.__name__}, not a {type(entity).__name__}.",
                )
            entity._chain_bind(entity=self)  # noqa: SLF001
        return entities[-1] if len(entities) == 1 else None

    def _chain_bind(self: EntityType, entity: EntityType) -> None:
        if self.__chain_root__:
            raise RuntimeError(
                f"{type(self).__name__} cannot be attached to another {self.__sub_name}.",
            )
        if not isinstance(entity, self.__entity):
            raise TypeError(
                f"The {self.__sub_name} must be an instance of "
                f"{self.__entity.__name__}, not a {type(entity).__name__}.",
            )
        if self.head:
            raise RuntimeError(
                f"The {self.__sub_name} name={self.name!r} is already attached to "
                f"{self.__sub_name} name={self.head.name!r}.",
            )
        if self == entity:
            raise ValueError(
                f"Cannot include the {self.__sub_name} on itself.",
            )
        if self in entity.chain_head:
            raise RuntimeError(
                "Circular referencing detected.",
            )
        self.head = entity
        entity.tail.append(self)
