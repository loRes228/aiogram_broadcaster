from datetime import timedelta
from typing import Iterable, List, Sequence, Union

from aiogram.types import (
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
)
from pydantic import BaseModel


ChatIdType = Union[int, str]
ChatIdsType = Union[Iterable[ChatIdType], Sequence[ChatIdType]]
IntervalType = Union[float, timedelta]
MarkupType = Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, None]


class SettingsData(BaseModel):
    message: Message
    reply_markup: MarkupType
    disable_notification: bool
    delay: float
    total_chats: int
    delete_on_complete: bool


class Data(BaseModel):
    chat_ids: List[int]
    settings: SettingsData

    @classmethod
    def build(
        cls,
        *,
        chat_ids: ChatIdsType,
        message: Message,
        reply_markup: MarkupType,
        disable_notification: bool,
        interval: IntervalType,
        dynamic_interval: bool,
        delete_on_complete: bool,
    ) -> "Data":
        chat_ids = list(set(chat_ids))
        total_chats = len(chat_ids)
        delay = validate_delay(
            interval=interval,
            dynamic=dynamic_interval,
            total_chats=total_chats,
        )
        return Data(
            chat_ids=chat_ids,
            settings=SettingsData(
                message=message,
                reply_markup=reply_markup,
                disable_notification=disable_notification,
                delay=delay,
                total_chats=total_chats,
                delete_on_complete=delete_on_complete,
            ),
        )


def validate_delay(
    interval: IntervalType,
    *,
    dynamic: bool,
    total_chats: int,
) -> float:
    if isinstance(interval, timedelta):
        interval = interval.total_seconds()
    if dynamic:
        return interval / total_chats
    return interval
