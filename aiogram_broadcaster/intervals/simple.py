from typing import TYPE_CHECKING

from pydantic import Field

from .base import BaseInterval


class SimpleInterval(BaseInterval):
    interval: float = Field(default=0, ge=0)

    async def __call__(self) -> float:
        return self.interval

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            interval: float = ...,
        ) -> None: ...
