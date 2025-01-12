from datetime import timedelta
from typing import TYPE_CHECKING

from pydantic import Field
from typing_extensions import Self

from .base import BaseInterval


class SimpleInterval(BaseInterval):
    interval: float = Field(default=0, ge=0)

    @classmethod
    def from_timedelta(cls, interval: timedelta) -> Self:
        return cls(interval=interval.total_seconds())

    async def __call__(self) -> float:
        return self.interval

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            interval: float = ...,
        ) -> None: ...
