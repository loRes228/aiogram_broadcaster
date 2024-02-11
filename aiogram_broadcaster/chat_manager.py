from enum import Enum, auto
from typing import TYPE_CHECKING, Optional, Set


if TYPE_CHECKING:
    from .settings import ChatIdsType, ChatsSettings
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

    def __getitem__(self, item: ChatState) -> Set[int]:
        return self.settings.chats[item]

    def get_chat(self, state: ChatState) -> int:
        return self.settings.chats[state].copy().pop()

    async def add_chats(self, chat_ids: "ChatIdsType") -> bool:
        exists_chats = set().union(*self.settings.chats.values())
        difference = set(chat_ids) - exists_chats
        if not difference:
            return False
        self.settings.chats[ChatState.PENDING].update(difference)
        if self.storage:
            await self.storage.set_chats_settings(
                mailer_id=self.mailer_id,
                settings=self.settings,
            )
        return True

    async def set_chat_state(self, chat: int, state: ChatState) -> None:
        chat_state = self._resolve_chat_state(chat=chat)
        self.settings.chats[chat_state].discard(chat)
        self.settings.chats[state].add(chat)
        if self.storage:
            await self.storage.set_chat_state(
                mailer_id=self.mailer_id,
                chat=chat,
                state=state,
            )

    def _resolve_chat_state(self, chat: int) -> ChatState:
        for state, state_chats in self.settings.chats.items():
            if chat in state_chats:
                return state
        raise LookupError
