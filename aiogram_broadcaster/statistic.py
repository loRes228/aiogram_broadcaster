from typing import NamedTuple, Set

from .chat_manager import ChatManager, ChatState


class Statistic(NamedTuple):
    pending_chats: Set[int]
    success_chats: Set[int]
    failed_chats: Set[int]

    @classmethod
    def from_chat_manager(cls, chat_manager: ChatManager, /) -> "Statistic":
        return Statistic(
            pending_chats=chat_manager[ChatState.PENDING],
            success_chats=chat_manager[ChatState.SUCCESS],
            failed_chats=chat_manager[ChatState.FAILED],
        )

    @property
    def total_count(self) -> int:
        return self.pending_count + self.success_count + self.failed_count

    @property
    def sends_count(self) -> int:
        return self.success_count + self.failed_count

    @property
    def pending_count(self) -> int:
        return len(self.pending_chats)

    @property
    def success_count(self) -> int:
        return len(self.success_chats)

    @property
    def failed_count(self) -> int:
        return len(self.failed_chats)

    @property
    def sends_ratio(self) -> float:
        return (self.sends_count / self.total_count) * 100

    @property
    def pending_ratio(self) -> float:
        return (self.pending_count / self.total_count) * 100

    @property
    def success_ratio(self) -> float:
        return (self.success_count / self.total_count) * 100

    @property
    def failed_ratio(self) -> float:
        return (self.failed_count / self.total_count) * 100

    def __repr__(self) -> str:
        return (
            "Statistic("
            f"total_count={self.total_count},"
            f"sends_count={self.sends_count},"
            f"pending_count={self.pending_count},"
            f"success_count={self.success_count},"
            f"failed_count={self.failed_count}"
            ")"
        )

    def __str__(self) -> str:
        return (
            f"Total: {self.total_count}\n"
            f"Sends: {self.sends_count} | {self.sends_ratio:.2f}%\n"
            f"Pending: {self.pending_count} | {self.pending_ratio:.2f}%\n"
            f"Success: {self.success_count} | {self.success_ratio:.2f}%\n"
            f"Failed: {self.failed_count} | {self.failed_ratio:.2f}%"
        )
