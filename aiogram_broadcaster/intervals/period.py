from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from pydantic import Field
from typing_extensions import Self

from aiogram_broadcaster.mailer.mailer import Mailer

from .base import BaseInterval


class PeriodInterval(BaseInterval):
    period: float = Field(default=1, ge=1)

    @classmethod
    def from_timedelta(cls, period: timedelta) -> Self:
        return cls(period=period.total_seconds())

    @classmethod
    def from_datetime(cls, period: datetime) -> Self:
        delta = period - datetime.now(tz=period.tzinfo)
        return cls(period=delta.total_seconds())

    async def __call__(self, mailer: Mailer) -> float:
        return self.period / len(mailer.chats.total)

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            period: float = ...,
        ) -> None: ...
