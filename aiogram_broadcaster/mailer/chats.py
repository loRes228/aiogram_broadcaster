from collections import defaultdict
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from enum import IntEnum, auto
from math import inf
from typing import SupportsInt

from pydantic import BaseModel, ConfigDict
from typing_extensions import Self


@dataclass(frozen=True)
class ChatsMetric:
    ids: set[int]

    def __str__(self) -> str:
        return str(len(self))

    def __repr__(self) -> str:
        return f"ChatsMetric(total={len(self)})"

    def __iter__(self) -> Iterator[int]:
        return iter(self.ids)

    def __contains__(self, item: int) -> bool:
        return item in self.ids

    def __bool__(self) -> bool:
        return bool(self.ids)

    def __len__(self) -> int:
        return len(self.ids)

    def __index__(self) -> int:
        return len(self)

    def __int__(self) -> int:
        return len(self)

    def __float__(self) -> float:
        return len(self)

    def __lt__(self, other: SupportsInt) -> bool:
        return int(self) < int(other)

    def __gt__(self, other: SupportsInt) -> bool:
        return int(self) > int(other)

    def __le__(self, other: SupportsInt) -> bool:
        return int(self) <= int(other)

    def __ge__(self, other: SupportsInt) -> bool:
        return int(self) >= int(other)

    def __mod__(self, other: SupportsInt) -> float:  # Same as ratio
        return self.ratio(other=other)

    def __sub__(self, other: SupportsInt) -> int:  # Same as difference
        return self.difference(other=other)

    def __add__(self, other: SupportsInt) -> float:  # Same as average
        return self.average(other=other)

    def ratio(self, other: SupportsInt) -> float:
        if int(other) == 0:
            return inf
        return (int(self) / int(other)) * 100

    def difference(self, other: SupportsInt) -> int:
        return abs(int(self) - int(other))

    def average(self, other: SupportsInt) -> float:
        return (int(self) + int(other)) / 2


class ChatState(IntEnum):
    PENDING = auto()
    FAILED = auto()
    SUCCESS = auto()


class Chats(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    registry: defaultdict[ChatState, set[int]]

    def __str__(self) -> str:
        metrics = [f"{metric_name}={len(metric)}" for metric_name, metric in self.metrics.items()]
        metrics_string = ", ".join(metrics)
        return f"Chats({metrics_string})"

    @classmethod
    def from_iterable(cls, iterable: Iterable[int]) -> Self:
        return cls(registry={ChatState.PENDING: set(iterable)})

    @property
    def total(self) -> ChatsMetric:
        chats = set().union(*(self.registry[state] for state in ChatState))
        return ChatsMetric(ids=chats)

    @property
    def processed(self) -> ChatsMetric:
        chats = set().union(self.registry[ChatState.FAILED], self.registry[ChatState.SUCCESS])
        return ChatsMetric(ids=chats)

    @property
    def pending(self) -> ChatsMetric:
        chats = self.registry[ChatState.PENDING].copy()
        return ChatsMetric(ids=chats)

    @property
    def failed(self) -> ChatsMetric:
        chats = self.registry[ChatState.FAILED].copy()
        return ChatsMetric(ids=chats)

    @property
    def success(self) -> ChatsMetric:
        chats = self.registry[ChatState.SUCCESS].copy()
        return ChatsMetric(ids=chats)

    @property
    def metrics(self) -> dict[str, ChatsMetric]:
        return {
            "total": self.total,
            "processed": self.processed,
            "pending": self.pending,
            "failed": self.failed,
            "success": self.success,
        }
