from typing import Any, ClassVar, Generator, List, Optional, Type, cast
from unittest.mock import sentinel

from typing_extensions import Self


UNSET_ENTITY = sentinel.UNSET_ENTITY


class ChainObject:
    __entity__: ClassVar[Type[Self]] = UNSET_ENTITY
    __sub_name__: ClassVar[str]
    __root__: ClassVar[bool]
    __name: str
    __parent_entity: Optional[Self]
    __sub_entities: List[Self]

    def __init_subclass__(cls, *, sub_name: Optional[str] = None, root: bool = False) -> None:
        if cls.__entity__ is UNSET_ENTITY:
            cls.__entity__ = cls
            cls.__sub_name__ = sub_name or cls.__name__.lower()
        cls.__root__ = root
        super().__init_subclass__()

    def __init__(self, name: Optional[str] = None) -> None:
        self.__name = name or hex(id(self))
        self.__parent_entity = None
        self.__sub_entities = []

    def __repr__(self) -> str:
        fields = [f"name={self.name!r}"]
        if self.__sub_entities:
            fields.append(f"sub_{self.__sub_name__}s={list(self.__sub_entities)}")
        fields_sting = ", ".join(fields)
        return f"{type(self).__name__}({fields_sting})"

    def __str__(self) -> str:
        fields = [f"name={self.name!r}"]
        if self.__parent_entity:
            fields.append(f"parent_{self.__sub_name__}={self.__parent_entity}")
        fields_sting = ", ".join(fields)
        return f"{type(self).__name__}({fields_sting})"

    @property
    def name(self) -> str:
        return self.__name

    @property
    def chain_head(self) -> Generator[Self, None, None]:
        entity: Optional[Self] = self
        while entity:
            yield entity
            entity = entity.__parent_entity  # noqa: SLF001

    @property
    def chain_tail(self) -> Generator[Self, None, None]:
        yield self
        for sub_entity in self.__sub_entities:
            yield from sub_entity.chain_tail

    def _set_parent_entity(self, entity: Self) -> None:
        if self.__root__:
            raise RuntimeError(
                f"{type(self).__name__} cannot be attached to another {self.__sub_name__}.",
            )
        if not isinstance(entity, self.__entity__):
            raise TypeError(
                f"The {self.__sub_name__} must be an instance of {self.__entity__.__name__}, "
                f"not a {type(entity).__name__}.",
            )
        if self.__parent_entity:
            raise RuntimeError(
                f"The {self.__sub_name__} {self.name} is already attached to "
                f"{self.__parent_entity.__sub_name__} {self.__parent_entity.name}.",
            )
        if self == entity:
            raise ValueError(f"Cannot include the {self.__sub_name__} on itself.")
        if self in entity.chain_head:
            raise RuntimeError("Circular referencing detected.")

        self.__parent_entity = entity
        entity.__sub_entities.append(self)  # noqa: SLF001

    def include(self, *args: Any) -> None:
        if not args:
            raise ValueError(f"At least one {self.__sub_name__} must be provided to include.")
        for entity in args:
            if not isinstance(entity, self.__entity__):
                raise TypeError(
                    f"The {self.__sub_name__} must be an instance of {self.__entity__.__name__}, "
                    f"not a {type(entity).__name__}.",
                )
            entity._set_parent_entity(entity=cast(Self, self))  # noqa: SLF001
