from enum import Enum, auto
from typing import Any, AsyncGenerator, DefaultDict, Dict, Iterable, Optional, Set

from pydantic import BaseModel, ConfigDict, Field

from aiogram_broadcaster.storage.base import BaseBCRStorage


class ChatState(str, Enum):
    PENDING = auto()
    SUCCESS = auto()
    FAILED = auto()


class ChatEngine(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    chats: DefaultDict[ChatState, Set[int]]
    mailer_id: Optional[int] = Field(default=None, exclude=True)
    storage: Optional[BaseBCRStorage] = Field(default=None, exclude=True)

    def model_post_init(self, __context: Dict[str, Any]) -> None:
        if not __context:
            return
        self.mailer_id = __context.get("mailer_id")
        self.storage = __context.get("storage")

    def __len__(self) -> int:
        return len(self.get_chats())

    @classmethod
    def from_iterable(
        cls,
        iterable: Iterable[int],
        state: ChatState,
        mailer_id: Optional[int] = None,
        storage: Optional[BaseBCRStorage] = None,
    ) -> "ChatEngine":
        return ChatEngine(
            chats={state: set(iterable)},
            mailer_id=mailer_id,
            storage=storage,
        )

    async def iterate_chats(self, state: ChatState) -> AsyncGenerator[int, None]:
        while self.chats[state]:
            yield self.chats[state].copy().pop()

    def get_chats(self, *states: ChatState) -> Set[int]:
        if len(states) == 1:
            state, *_ = states
            return self.chats[state]
        chats = (self.chats[state] for state in states or ChatState)
        return set().union(*chats)

    async def add_chats(self, chats: Iterable[int], state: ChatState) -> Set[int]:
        difference = set(chats) - self.get_chats()
        if not difference:
            return difference
        self.chats[state].update(difference)
        await self._preserve()
        return difference

    async def set_chats_state(self, state: ChatState) -> None:
        chats = self.get_chats()
        self.chats.clear()
        self.chats[state] = chats
        await self._preserve()

    async def set_chat_state(self, chat: int, state: ChatState) -> None:
        from_state = self._resolve_chat_state(chat=chat)
        self.chats[from_state].discard(chat)
        self.chats[state].add(chat)
        await self._preserve()

    def _resolve_chat_state(self, chat: int) -> ChatState:
        for state, chats in self.chats.items():
            if chat in chats:
                return state
        raise LookupError(f"Chat={chats} state is undefined.")

    async def _preserve(self) -> None:
        if not self.storage or not self.mailer_id:
            return
        async with self.storage.update_record(mailer_id=self.mailer_id) as record:
            record.chats = self
