from collections import defaultdict
from enum import Enum, auto
from typing import AsyncGenerator, DefaultDict, Dict, Iterable, Mapping, Optional, Set

from pydantic import BaseModel, ConfigDict, Field

from aiogram_broadcaster.storage.base import BaseBCRStorage


class ChatState(str, Enum):
    PENDING = auto()
    SUCCESS = auto()
    FAILED = auto()


class ChatEngine(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    chats: DefaultDict[ChatState, Set[int]]
    mailer_id: int = Field(exclude=True)
    storage: Optional[BaseBCRStorage] = Field(default=None, exclude=True)

    def __len__(self) -> int:
        return len(self.get_chats())

    @classmethod
    def from_iterable(
        cls,
        iterable: Iterable[int],
        state: ChatState,
        mailer_id: int,
        storage: Optional[BaseBCRStorage] = None,
    ) -> "ChatEngine":
        return ChatEngine(
            chats={state: set(iterable)},
            mailer_id=mailer_id,
            storage=storage,
        )

    @classmethod
    def from_mapping(
        cls,
        mapping: Mapping[str, str],
        mailer_id: int,
        storage: Optional[BaseBCRStorage] = None,
    ) -> "ChatEngine":
        chats: Dict[str, Set[str]] = defaultdict(set)
        for chat, state in mapping.items():
            chats[state].add(chat)
        return ChatEngine(
            chats=chats,
            mailer_id=mailer_id,
            storage=storage,
        )

    def to_dict(self) -> Dict[str, str]:
        # fmt: off
        return {
            str(chat): str(state.value)
            for state, chats in self.chats.items()
            for chat in chats
        }
        # fmt: on

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
        if self.storage:
            await self.storage.set_chats(
                mailer_id=self.mailer_id,
                chats=self,
            )
        return difference

    async def set_chat_state(self, chat: int, state: ChatState) -> None:
        from_state = self.resolve_chat_state(chat=chat)
        self.chats[from_state].discard(chat)
        self.chats[state].add(chat)
        if self.storage:
            await self.storage.set_chat_state(
                mailer_id=self.mailer_id,
                chat=chat,
                state=state,
            )

    def resolve_chat_state(self, chat: int) -> ChatState:
        for state, chats in self.chats.items():
            if chat in chats:
                return state
        raise LookupError(f"Chat={chats} state is undefined.")
