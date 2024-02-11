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
        difference = self._get_difference(chats=set(chat_ids))
        if not difference:
            return False
        self.settings.chats[ChatState.PENDING].update(difference)
        if self.storage:
            await self.storage.set_chats_settings(
                mailer_id=self.mailer_id,
                settings=self.settings,
            )
        return True

    def _get_difference(self, chats: Set[int]) -> Set[int]:
        exists_chats = set().union(*self.settings.chats.values())
        return chats.difference(exists_chats)

    async def set_chat_state(self, chat: int, state: ChatState) -> None:
        self._move_chat_to_state(chat=chat, to_state=state)
        if self.storage:
            await self.storage.set_chat_state(
                mailer_id=self.mailer_id,
                chat=chat,
                state=state,
            )

    def _move_chat_to_state(self, chat: int, to_state: ChatState) -> None:
        from_state = self._resolve_chat_state(chat=chat)
        self.settings.chats[from_state].discard(chat)
        self.settings.chats[to_state].add(chat)

    def _resolve_chat_state(self, chat: int) -> ChatState:
        for state, chats in self.settings.chats.items():
            if chat in chats:
                return state
        raise LookupError
