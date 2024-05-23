from typing import Any, ClassVar, Generator, Generic, List, Optional, TypeVar, overload
from unittest.mock import sentinel


EntityType = TypeVar("EntityType", bound="ChainObject[Any]")

UNSET_ENTITY = sentinel.UNSET_ENTITY


class ChainObject(Generic[EntityType]):
    __chain_entity__: EntityType
    __chain_sub_name__: ClassVar[str]
    __chain_root__: ClassVar[bool]
    name: str
    head: Optional[EntityType]
    tail: List[EntityType]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        if not hasattr(cls, "__chain_entity__"):
            cls.__chain_root__ = False
            cls.__chain_entity__ = cls
            cls.__chain_sub_name__ = kwargs.pop("sub_name", cls.__name__.lower())
        super().__init_subclass__(**kwargs)

    def __init__(self, name: Optional[str] = None) -> None:
        self.name = hex(id(self)) if name is None else name
        self.head = None
        self.tail = []

    def __repr__(self) -> str:
        fields = []
        fields.append(f"name={self.name!r}")
        if self.tail:
            fields.append(f"nested={list(self.tail)!r}")
        fields_sting = ", ".join(fields)
        return f"{type(self).__name__}({fields_sting})"

    def __str__(self) -> str:
        fields = []
        fields.append(f"name={self.name!r}")
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
                f"At least one {self.__chain_sub_name__} must be provided to include.",
            )
        for entity in entities:
            if not isinstance(entity, self.__chain_entity__):
                raise TypeError(
                    f"The {self.__chain_sub_name__} must be an instance of "
                    f"{self.__chain_entity__.__name__}, not a {type(entity).__name__}.",
                )
            entity._chain_bind(entity=self)  # noqa: SLF001
        return entities[-1] if len(entities) == 1 else None

    def _chain_bind(self: EntityType, entity: EntityType) -> None:
        if self == entity:
            raise ValueError(
                f"Cannot include the {self.__chain_sub_name__} on itself.",
            )
        if self.head:
            raise RuntimeError(
                f"The {self.__chain_entity__.__name__}(name={self.name!r}) is already attached to "
                f"{self.__chain_entity__.__name__}(name={self.head.name!r}).",
            )
        if self in entity.chain_head:
            raise RuntimeError(
                "Circular referencing detected.",
            )
        if self.__chain_root__:
            raise RuntimeError(
                f"{type(self).__name__} cannot be attached to another {self.__chain_sub_name__}.",
            )
        self.head = entity
        entity.tail.append(self)
