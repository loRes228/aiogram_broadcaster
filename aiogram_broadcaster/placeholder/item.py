from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, ClassVar

from .placeholder import Placeholder


class PlaceholderItem(ABC):
    key: ClassVar[str]

    def __init_subclass__(cls, key: str, **kwargs: Any) -> None:
        cls.key = key
        super().__init_subclass__(**kwargs)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(key={self.key!r})"

    if TYPE_CHECKING:
        __call__: Callable[..., Any]
    else:

        @abstractmethod
        async def __call__(self, **kwargs: Any) -> Any:
            pass

    def as_placeholder(self) -> Placeholder:
        return Placeholder(key=self.key, value=self.__call__)
