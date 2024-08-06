from collections.abc import Generator
from typing import Any, ClassVar, Generic, Optional, TypeVar

from typing_extensions import Self


ChainType = TypeVar("ChainType", bound="Chain[Any]")


class ChainBindError(Exception):
    pass


class Chain(Generic[ChainType]):
    __chain_object__: ChainType
    __chain_root__: ClassVar[bool]
    __chain_sub_name__: ClassVar[str]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        if not hasattr(cls, "__chain_object__"):
            cls.__chain_object__ = cls
            cls.__chain_root__ = False
            cls.__chain_sub_name__ = kwargs.pop("sub_name", cls.__name__.lower())
        super().__init_subclass__(**kwargs)

    def __init__(self, name: Optional[str] = None) -> None:
        self.name = hex(id(self)) if name is None else name
        self.head: Optional[ChainType] = None
        self.tail: list[ChainType] = []

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name='{self.name}')"

    @property
    def chain_head(self: ChainType) -> Generator[ChainType, None, None]:
        chain: Optional[ChainType] = self
        while chain:
            yield chain
            chain = chain.head

    @property
    def chain_tail(self: ChainType) -> Generator[ChainType, None, None]:
        yield self
        for chain in self.tail:
            yield from chain.chain_tail

    def bind(self, *chains: ChainType) -> Self:
        if not chains:
            raise ValueError(f"At least one {self.__chain_sub_name__} must be provided to bind.")
        for chain in chains:
            if self == chain:
                raise ChainBindError(f"Cannot bind a {chain} to itself.")
            if chain.head:
                raise ChainBindError(f"The {chain} is already bound to {chain.head}.")
            if chain in self.chain_head:
                raise ChainBindError(
                    f"The {chain} is already part of {self.__chain_sub_name__} sequence.",
                )
            if chain.__chain_root__:
                raise ChainBindError(
                    f"Cannot bind the {chain} to another {self.__chain_sub_name__}.",
                )
            chain.head = self
            self.tail.append(chain)
        return self
