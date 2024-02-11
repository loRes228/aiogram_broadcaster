from typing import NamedTuple

from .chat_manager import ChatManager, ChatState


class Statistic(NamedTuple):
    pending: int
    success: int
    failed: int

    @classmethod
    def from_chat_manager(cls, chat_manager: ChatManager, /) -> "Statistic":
        return Statistic(
            pending=len(chat_manager[ChatState.PENDING]),
            success=len(chat_manager[ChatState.SUCCESS]),
            failed=len(chat_manager[ChatState.FAILED]),
        )

    @property
    def total(self) -> int:
        return self.pending + self.success + self.failed

    @property
    def total_ratio(self) -> float:
        return ((self.success + self.failed) / self.total) * 100

    @property
    def pending_ratio(self) -> float:
        return (self.pending / self.total) * 100

    @property
    def success_ratio(self) -> float:
        return (self.success / self.total) * 100

    @property
    def failed_ratio(self) -> float:
        return (self.failed / self.total) * 100
