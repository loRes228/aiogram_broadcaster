from typing import Any, ClassVar, Generator, List, Optional, Type, cast
from unittest.mock import sentinel

from typing_extensions import Self


UNSET_ENTITY = sentinel.UNSET_ENTITY


class ChainObject:
    __chain_root__: ClassVar[bool] = False
    __entity__: ClassVar[Type[Self]] = UNSET_ENTITY
    __singular_name__: ClassVar[str]
    __plural_name__: ClassVar[str]
    name: str
    head: Optional[Self]
    tail: List[Self]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        if cls.__entity__ is UNSET_ENTITY:
            cls.__entity__ = cls
            cls.__singular_name__ = kwargs.pop("singular_name", cls.__name__.lower())
            cls.__plural_name__ = kwargs.pop("plural_name", f"{cls.__name__.lower()}s")
        super().__init_subclass__(**kwargs)

    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name or hex(id(self))
        self.head = None
        self.tail = []

    def __repr__(self) -> str:
        fields = [f"name={self.name!r}"]
        if self.tail:
            fields.append(f"sub_{self.__plural_name__}={list(self.tail)}")
        fields_sting = ", ".join(fields)
        return f"{type(self).__name__}({fields_sting})"

    def __str__(self) -> str:
        fields = [f"name={self.name!r}"]
        if self.head:
            fields.append(f"parent_{self.__singular_name__}={self.head}")
        fields_sting = ", ".join(fields)
        return f"{type(self).__name__}({fields_sting})"

    @property
    def chain_head(self) -> Generator[Self, None, None]:
        entity: Optional[Self] = self
        while entity:
            yield entity
            entity = entity.head

    @property
    def chain_tail(self) -> Generator[Self, None, None]:
        yield self
        for entity in self.tail:
            yield from entity.chain_tail

    def include(self, *args: Any) -> None:
        if not args:
            raise ValueError(
                f"At least one {self.__singular_name__} must be provided to include.",
            )
        for entity in args:
            if not isinstance(entity, self.__entity__):
                raise TypeError(
                    f"The {self.__singular_name__} must be an instance of "
                    f"{self.__entity__.__name__}, not a {type(entity).__name__}.",
                )
            entity._set_head(entity=cast(Self, self))  # noqa: SLF001

    def _set_head(self, entity: Self) -> None:
        if self.__chain_root__:
            raise RuntimeError(
                f"{type(self).__name__} cannot be attached to another {self.__singular_name__}.",
            )
        if not isinstance(entity, self.__entity__):
            raise TypeError(
                f"The {self.__singular_name__} must be an instance of "
                f"{self.__entity__.__name__}, not a {type(entity).__name__}.",
            )
        if self.head:
            raise RuntimeError(
                f"The {self.__singular_name__} {self.name} is already attached to "
                f"{self.__singular_name__} {self.head.name}.",
            )
        if self == entity:
            raise ValueError(
                f"Cannot include the {self.__singular_name__} on itself.",
            )
        if self in entity.chain_head:
            raise RuntimeError(
                "Circular referencing detected.",
            )

        self.head = entity
        entity.tail.append(self)
