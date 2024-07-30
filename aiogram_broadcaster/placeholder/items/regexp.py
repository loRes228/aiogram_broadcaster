from enum import Enum
from re import Pattern, RegexFlag, compile
from typing import Any, Union

from .base import BasePlaceholderItem, RenderResult


class RegexMode(str, Enum):
    SEARCH = "search"
    MATCH = "match"
    FULLMATCH = "fullmatch"
    FINDALL = "findall"
    FINDITER = "finditer"


class RegexpPlaceholderItem(BasePlaceholderItem):
    pattern: Pattern[str]
    flags: Union[int, RegexFlag]
    mode: RegexMode

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

    def _render(self, source: str) -> RenderResult:
        match: Any = getattr(self.pattern, self.mode.value)(source)
        if not match:
            return None
        return {"match": match}, lambda value: self.pattern.sub(repl=value, string=source)
