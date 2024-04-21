from enum import Enum, auto
from typing import TYPE_CHECKING, AsyncGenerator, DefaultDict, Iterable, Optional, Set

from pydantic import BaseModel, ConfigDict


if TYPE_CHECKING:
    from aiogram_broadcaster.storage.base import BaseMailerStorage


class ChatState(str, Enum):
    PENDING = auto()
    SUCCESS = auto()
    FAILED = auto()


class ChatsRegistry(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    chats: DefaultDict[ChatState, Set[int]]

    @classmethod
    def from_iterable(
        cls,
        chats: Iterable[int],
        state: ChatState = ChatState.PENDING,
    ) -> "ChatsRegistry":
        return ChatsRegistry(chats={state: chats})


class ChatEngine:
    registry: ChatsRegistry
    mailer_id: Optional[int]
    storage: Optional["BaseMailerStorage"]

    def __init__(
        self,
        registry: ChatsRegistry,
        mailer_id: Optional[int] = None,
        storage: Optional["BaseMailerStorage"] = None,
    ) -> None:
        self.registry = registry
        self.mailer_id = mailer_id
        self.storage = storage

    async def iterate_chats(self, state: ChatState) -> AsyncGenerator[int, None]:
        while self.registry.chats[state]:
            yield self.registry.chats[state].copy().pop()

    def get_chats(self, *states: ChatState) -> Set[int]:
        if len(states) == 1:
            return self.registry.chats[states[-1]]
        chats = (self.registry.chats[state] for state in states or ChatState)
        return set().union(*chats)

    async def add_chats(self, chats: Iterable[int], state: ChatState) -> Set[int]:
        difference = set(chats) - self.get_chats()
        if not difference:
            return set()
        self.registry.chats[state].update(difference)
        await self._preserve()
        return difference

    async def set_chats_state(self, state: ChatState) -> bool:
        chats = self.get_chats()
        if self.registry.chats[state] == chats:
            return False
        self.registry.chats.clear()
        self.registry.chats[state] = chats
        await self._preserve()
        return True

    async def set_chat_state(self, chat: int, state: ChatState) -> None:
        from_state = self._resolve_chat_state(chat=chat)
        self.registry.chats[from_state].remove(chat)
        self.registry.chats[state].add(chat)
        await self._preserve()

    def _resolve_chat_state(self, chat: int) -> ChatState:
        for state, chats in self.registry.chats.items():
            if chat in chats:
                return state
        raise LookupError(f"State of chat={chat} could not be resolved.")

    async def _preserve(self) -> None:
        if not self.storage or not self.mailer_id:
            return
        async with self.storage.update(mailer_id=self.mailer_id) as record:
            record.chats = self.registry
