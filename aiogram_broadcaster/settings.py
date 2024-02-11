from collections import defaultdict
from datetime import timedelta
from typing import DefaultDict, Dict, Iterable, Iterator, Sequence, Set, Union

from aiogram.types import InlineKeyboardMarkup, Message, ReplyKeyboardMarkup
from pydantic import BaseModel, ConfigDict

from .chat_manager import ChatState
from .enums import Strategy


ChatIdsType = Union[Iterable[int], Iterator[int], Sequence[int]]
ChatsType = DefaultDict[ChatState, Set[int]]
IntervalType = Union[float, timedelta]
ReplyMarkupType = Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, None]


class ChatsSettings(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    chats: ChatsType

    @classmethod
    def from_raw_mapping(cls, mapping: Dict[int, str]) -> "ChatsSettings":
        chats: ChatsType = defaultdict(set)
        for chat, chat_state in mapping.items():
            chats[ChatState(chat_state)].add(chat)
        return ChatsSettings(chats=chats)

    def to_raw_mapping(self) -> Dict[int, str]:
        return {
            chat: str(state.value)  # fmt: skip
            for state, chats in self.chats.items()
            for chat in chats
        }


class MailerSettings(BaseModel):
    strategy: Strategy = Strategy.SEND
    delay: float = 1
    disable_events: bool = False
    delete_on_complete: bool = False


class MessageSettings(BaseModel):
    message: Message
    reply_markup: ReplyMarkupType = None
    disable_notification: bool = False
    protect_content: bool = False


class Settings(BaseModel):
    chats: ChatsSettings
    mailer: MailerSettings
    message: MessageSettings

    @classmethod
    def build(
        cls,
        *,
        chat_ids: ChatIdsType,
        message: Message,
        reply_markup: ReplyMarkupType,
        disable_notification: bool,
        protect_content: bool,
        strategy: Strategy,
        interval: IntervalType,
        dynamic_interval: bool,
        disable_events: bool,
        delete_on_complete: bool,
    ) -> "Settings":
        if isinstance(interval, timedelta):
            interval = interval.total_seconds()

        chats = set(chat_ids)
        delay = (
            interval / len(chats)  # fmt: skip
            if dynamic_interval
            else interval
        )

        return Settings(
            chats=ChatsSettings(
                chats={ChatState.PENDING: chats},
            ),
            mailer=MailerSettings(
                strategy=strategy,
                delay=delay,
                disable_events=disable_events,
                delete_on_complete=delete_on_complete,
            ),
            message=MessageSettings(
                message=message,
                reply_markup=reply_markup,
                disable_notification=disable_notification,
                protect_content=protect_content,
            ),
        )
