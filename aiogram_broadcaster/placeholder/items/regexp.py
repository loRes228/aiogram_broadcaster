from enum import Enum
from re import Pattern, RegexFlag, compile
from typing import TYPE_CHECKING, Any, Callable, Union

from .base import BasePlaceholderDecorator, BasePlaceholderEngine, BasePlaceholderItem


if TYPE_CHECKING:
    from typing_extensions import Self


class RegexMode(str, Enum):
    SEARCH = "search"
    MATCH = "match"
    FULLMATCH = "fullmatch"
    FINDALL = "findall"
    FINDITER = "finditer"


class RegexpPlaceholderItem(BasePlaceholderItem):
    def __init__(
        self,
        value: Any,
        pattern: Union[str, Pattern[str]],
        flags: Union[int, RegexFlag] = 0,
        mode: RegexMode = RegexMode.MATCH,
    ) -> None:
        super().__init__(value=value)

        self.pattern = (
            compile(pattern=pattern, flags=flags) if isinstance(pattern, str) else pattern
        )
        self.flags = flags
        self.mode = mode


class RegexpPlaceholderDecorator(BasePlaceholderDecorator):
    __item_class__ = RegexpPlaceholderItem

    if TYPE_CHECKING:

        def __call__(
            self,
            pattern: Union[str, Pattern[str]],
            flags: Union[int, RegexFlag] = ...,
            mode: RegexMode = ...,
        ) -> Callable[[Callable[..., Any]], Callable[..., Any]]: ...

        def register(
            self,
            value: Any,
            pattern: Union[str, Pattern[str]],
            flags: Union[int, RegexFlag] = ...,
            mode: RegexMode = ...,
        ) -> Self: ...


class RegexpPlaceholderEngine(BasePlaceholderEngine):
    async def render(self, source: str, *items: RegexpPlaceholderItem, **context: Any) -> str:
        for item in items:
            regex_method = getattr(item.pattern, item.mode.value)
            match = regex_method(source)
            if not match:
                continue
            value = await item.get_value(match=match, **context)
            if value is not None:
                source = item.pattern.sub(repl=value, string=source)
        return source
