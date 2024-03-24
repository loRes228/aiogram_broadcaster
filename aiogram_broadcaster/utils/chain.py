from typing import TYPE_CHECKING, Callable, ClassVar, Generator, List, Optional, Type

from typing_extensions import Self


class ChainObject:
    __chain_root__: ClassVar[bool] = False
    __entity: Type[Self]
    __sub_name: str
    __parent_entity: Optional[Self]
    __sub_entities: List[Self]

    def __init__(self, entity: Type[Self], sub_name: str) -> None:
        if not issubclass(entity, ChainObject):
            raise TypeError(
                f"The entity must be a subclass of ChainObject, not a {entity.__name__}.",
            )
        self.__entity = entity
        self.__sub_name = sub_name
        self.__parent_entity = None
        self.__sub_entities = []

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
        if self.__chain_root__:
            raise RuntimeError(
                f"{type(self).__name__} cannot be attached to another {self.__sub_name}.",
            )
        if not isinstance(entity, self.__entity):
            raise TypeError(
                f"The {self.__sub_name} must be an instance of {self.__entity.__name__}, "
                f"not a {type(entity).__name__}.",
            )
        if self.__parent_entity:
            raise RuntimeError(
                f"The {self.__sub_name} is already attached to {self.__parent_entity!r}.",
            )
        if self == entity:
            raise ValueError(f"Cannot include {self.__sub_name} on itself.")
        if self in entity.chain_head:
            raise RuntimeError("Circular referencing detected.")

        self.__parent_entity = entity
        entity.__sub_entities.append(self)  # noqa: SLF001

    if TYPE_CHECKING:
        include: Callable[..., None]
    else:

        def include(self, *args: Self) -> None:
            if not args:
                raise ValueError(f"At least one {self.__sub_name} must be provided to include.")
            for entity in args:
                if not isinstance(entity, self.__entity):
                    raise TypeError(
                        f"The {self.__sub_name} must be an instance of {self.__entity.__name__}, "
                        f"not a {type(entity).__name__}.",
                    )
                entity._set_parent_entity(entity=self)  # noqa: SLF001
