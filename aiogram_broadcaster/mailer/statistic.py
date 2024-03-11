from typing import Set

from .chat_manager import ChatManager, ChatState


class MailerStatistic:
    def __init__(self, chat_manager: ChatManager) -> None:
        self._chat_manager = chat_manager

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"total_count={self.total_count}"
            f"pending_count={self.pending_count}"
            f"success_count={self.success_count}"
            f"failed_count={self.failed_count}"
            f"sends_count={self.sends_count}"
            ")"
        )

    def __str__(self) -> str:
        return (
            f"Total chats: {self.total_count}\n"
            f"Pending chats: {self.pending_count} | {self.pending_ratio:.2f}%\n"
            f"Success chats: {self.success_count} | {self.success_ratio:.2f}%\n"
            f"Failed chats: {self.failed_count} | {self.failed_ratio:.2f}%\n"
            f"Sends chats: {self.sends_count} | {self.sends_ratio:.2f}%"
        )

    @property
    def total_chats(self) -> Set[int]:
        return self._chat_manager.get_chats()

    @property
    def pending_chats(self) -> Set[int]:
        return self._chat_manager.get_chats(ChatState.PENDING)

    @property
    def success_chats(self) -> Set[int]:
        return self._chat_manager.get_chats(ChatState.SUCCESS)

    @property
    def failed_chats(self) -> Set[int]:
        return self._chat_manager.get_chats(ChatState.FAILED)

    @property
    def sends_chats(self) -> Set[int]:
        return self._chat_manager.get_chats(ChatState.SUCCESS, ChatState.FAILED)

    @property
    def total_count(self) -> int:
        return len(self.total_chats)

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
    def sends_count(self) -> int:
        return len(self.sends_chats)

    @property
    def pending_ratio(self) -> float:
        return self._calculate_ratio(self.pending_count)

    @property
    def success_ratio(self) -> float:
        return self._calculate_ratio(self.success_count)

    @property
    def failed_ratio(self) -> float:
        return self._calculate_ratio(self.failed_count)

    @property
    def sends_ratio(self) -> float:
        return self._calculate_ratio(self.sends_count)

    def _calculate_ratio(self, value: int) -> float:
        return (value / self.total_count) * 100
