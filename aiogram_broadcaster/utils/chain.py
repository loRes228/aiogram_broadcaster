from typing import Any, ClassVar, Generator, Generic, List, Optional, TypeVar, overload
from unittest.mock import sentinel


UNSET_ENTITY = sentinel.UNSET_ENTITY

EntityType = TypeVar("EntityType", bound=Any)


class ChainObject(Generic[EntityType]):
    __chain_root__: ClassVar[bool] = False
    __entity__: EntityType = UNSET_ENTITY
    __sub_name__: ClassVar[str]
    name: str
    head: Optional[EntityType]
    tail: List[EntityType]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        if cls.__entity__ is UNSET_ENTITY:
            cls.__entity__ = cls
            cls.__sub_name__ = kwargs.pop("sub_name", cls.__name__.lower())
        super().__init_subclass__(**kwargs)

    def __init__(self, name: Optional[str] = None) -> None:
        if name is None:
            name = hex(id(self))
        self.name = name
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
    def include(self, entity: EntityType, /) -> EntityType:
        pass

    @overload
    def include(self, *entities: EntityType) -> None:
        pass

    def include(self: "ChainObject[Any]", *entities: "ChainObject[Any]") -> Any:
        if not entities:
            raise ValueError(
                f"At least one {self.__sub_name__} must be provided to include.",
            )
        for entity in entities:
            if not isinstance(entity, self.__entity__):
                raise TypeError(
                    f"The {self.__sub_name__} must be an instance of "
                    f"{self.__entity__.__name__}, not a {type(entity).__name__}.",
                )
            entity._chain_bind(entity=self)  # noqa: SLF001
        if len(entities) == 1:
            return entities[-1]
        return None

    def _chain_bind(self: "ChainObject[Any]", entity: "ChainObject[Any]") -> None:
        if self.__chain_root__:
            raise RuntimeError(
                f"{type(self).__name__} cannot be attached to another {self.__sub_name__}.",
            )
        if not isinstance(entity, self.__entity__):
            raise TypeError(
                f"The {self.__sub_name__} must be an instance of "
                f"{self.__entity__.__name__}, not a {type(entity).__name__}.",
            )
        if self.head:
            raise RuntimeError(
                f"The {self.__sub_name__} name={self.name!r} is already attached to "
                f"{self.__sub_name__} name={self.head.name!r}.",
            )
        if self == entity:
            raise ValueError(
                f"Cannot include the {self.__sub_name__} on itself.",
            )
        if self in entity.chain_head:
            raise RuntimeError(
                "Circular referencing detected.",
            )
        self.head = entity
        entity.tail.append(self)
