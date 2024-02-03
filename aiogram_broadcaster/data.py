from datetime import timedelta
from typing import Iterable, List, Optional, Sequence, Union

from aiogram.types import InlineKeyboardMarkup, Message
from pydantic import BaseModel


ChatId = Union[int, str]
ChatIds = Union[Iterable[ChatId], Sequence[ChatId]]
ReplyMarkup = Optional[InlineKeyboardMarkup]
Interval = Union[float, int, timedelta]


class SettingsData(BaseModel):
    message: Message
    reply_markup: ReplyMarkup
    disable_notification: bool
    delay: float
    total_chats: int


class Data(BaseModel):
    chat_ids: List[int]
    settings: SettingsData

    @classmethod
    def build(
        cls,
        *,
        chat_ids: ChatIds,
        message: Message,
        reply_markup: ReplyMarkup,
        disable_notification: bool,
        interval: Interval,
        dynamic_interval: bool,
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
            ),
        )

    @classmethod
    def build_from_json(
        cls,
        *,
        chat_ids: List[int],
        settings: str,
    ) -> "Data":
        return Data(
            chat_ids=chat_ids,
            settings=SettingsData.model_validate_json(settings),
        )


def validate_delay(
    interval: Interval,
    *,
    dynamic: bool,
    total_chats: int,
) -> float:
    interval = (
        interval.total_seconds()  # fmt: skip
        if isinstance(interval, timedelta)
        else float(interval)
    )
    if dynamic:
        return dynamic / total_chats
    return interval
