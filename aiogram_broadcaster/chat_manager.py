from enum import Enum, auto
from typing import TYPE_CHECKING, Optional, Tuple


if TYPE_CHECKING:
    from .settings import ChatsSettings
    from .storage.base import BaseMailerStorage


# Enum values are strings to prevent `ValidationError` when retrieving data from Redis.
class ChatState(str, Enum):
    PENDING = auto()
    SUCCESS = auto()
    FAILED = auto()


class ChatManager:
    mailer_id: int
    storage: Optional["BaseMailerStorage"]
    settings: "ChatsSettings"

    __slots__ = (
        "mailer_id",
        "settings",
        "storage",
    )

    def __init__(
        self,
        mailer_id: int,
        storage: Optional["BaseMailerStorage"],
        settings: "ChatsSettings",
    ) -> None:
        self.mailer_id = mailer_id
        self.storage = storage
        self.settings = settings

    def has_chats(self, state: ChatState) -> bool:
        return state in self.settings.chats.values()

    def get_chats_count(self, state: ChatState) -> int:
        return len(self.get_chats(state=state))

    def get_chats(self, state: ChatState) -> Tuple[int, ...]:
        return tuple(
            chat  # fmt: skip
            for chat, chat_state in self.settings.chats.items()
            if chat_state == state
        )

    async def set_state(self, chat: int, state: ChatState) -> None:
        self.settings.chats[chat] = state
        if self.storage:
            await self.storage.set_chat_state(
                mailer_id=self.mailer_id,
                chat=chat,
                state=state,
            )
