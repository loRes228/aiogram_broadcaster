from typing import Dict, Iterator, Set, SupportsInt

from .chat_engine import ChatEngine, ChatState


class ChatsMetric:
    ids: Set[int]
    total: int
    ratio: float
    average: float
    range: float
    relative_range: float
    metrics: Dict[str, float]

    def __init__(self, ids: Set[int], total: int) -> None:
        self.ids = ids
        self.total = len(ids)
        self.ratio = (self.total / total) * 100
        self.average = (self.total + total) / 2
        self.range = abs(self.total - total)
        self.relative_range = (self.range / self.average) * 100
        self.metrics = {
            "total": self.total,
            "ratio": self.ratio,
            "average": self.average,
            "range": self.range,
            "relative_range": self.relative_range,
        }

    def __repr__(self) -> str:
        # fmt: off
        metrics = ", ".join(
            f"{metric_name}={metric}"
            for metric_name, metric in self.metrics.items()
        )
        # fmt: on
        return f"ChatsStatistic({metrics})"

    def __str__(self) -> str:
        # fmt: off
        return ", ".join(
            f"{metric_name.replace('_', ' ')}: {metric}"
            for metric_name, metric in self.metrics.items()
        )
        # fmt: on

    def __getitem__(self, item: str) -> float:
        return self.metrics[item]

    def __iter__(self) -> Iterator[int]:
        return iter(self.ids)

    def __contains__(self, item: int) -> bool:
        return item in self.ids

    def __len__(self) -> int:
        return self.total

    def __int__(self) -> int:
        return self.total

    def __bool__(self) -> bool:
        return self.range == 0

    def __lt__(self, other: SupportsInt) -> bool:
        return self.total < int(other)

    def __gt__(self, other: SupportsInt) -> bool:
        return self.total > int(other)

    def __le__(self, other: SupportsInt) -> bool:
        return self.total <= int(other)

    def __ge__(self, other: SupportsInt) -> bool:
        return self.total >= int(other)


class MailerStatistic:
    _chat_engine: ChatEngine

    def __init__(self, chat_engine: ChatEngine) -> None:
        self._chat_engine = chat_engine

    def __repr__(self) -> str:
        # fmt: off
        metrics = ", ".join(
            f"{metric_name}={metric.total}"
            for metric_name, metric in self.metrics.items()
        )
        # fmt: on
        return f"MailerStatistic({metrics})"

    def __str__(self) -> str:
        return "\n".join(
            f"{metric_name.replace('_', ' ').capitalize()} - {metric}"
            for metric_name, metric in self.metrics.items()
        )

    def __getitem__(self, item: str) -> ChatsMetric:
        return self.metrics[item]

    @property
    def total_chats(self) -> ChatsMetric:
        chats = self._chat_engine.get_chats()
        return ChatsMetric(ids=chats, total=len(chats))

    @property
    def pending_chats(self) -> ChatsMetric:
        chats = self._chat_engine.get_chats(ChatState.PENDING)
        return ChatsMetric(ids=chats, total=self.total_chats.total)

    @property
    def success_chats(self) -> ChatsMetric:
        chats = self._chat_engine.get_chats(ChatState.SUCCESS)
        return ChatsMetric(ids=chats, total=self.total_chats.total)

    @property
    def failed_chats(self) -> ChatsMetric:
        chats = self._chat_engine.get_chats(ChatState.FAILED)
        return ChatsMetric(ids=chats, total=self.total_chats.total)

    @property
    def processed_chats(self) -> ChatsMetric:
        chats = self._chat_engine.get_chats(ChatState.SUCCESS, ChatState.FAILED)
        return ChatsMetric(ids=chats, total=self.total_chats.total)

    @property
    def metrics(self) -> Dict[str, ChatsMetric]:
        return {
            "total_chats": self.total_chats,
            "pending_chats": self.pending_chats,
            "success_chats": self.success_chats,
            "failed_chats": self.failed_chats,
            "processed_chats": self.processed_chats,
        }
