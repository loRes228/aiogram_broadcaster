from datetime import timedelta
from typing import Iterable, List, NamedTuple, Optional, Sequence, Union

from aiogram.types import InlineKeyboardMarkup, Message
from pydantic import BaseModel


ChatIds = Union[Iterable[Union[int, str]], Sequence[Union[int, str]]]
ReplyMarkup = Optional[InlineKeyboardMarkup]
Interval = Union[float, int, timedelta]


class MailerSettingsData(BaseModel):
    message: Message
    reply_markup: ReplyMarkup
    disable_notification: bool
    interval: float
    total_chats: int


class MailerData(BaseModel):
    chat_ids: List[int]
    settings: MailerSettingsData

    @classmethod
    def build(
        cls,
        *,
        chat_ids: ChatIds,
        message: Message,
        reply_markup: ReplyMarkup,
        disable_notification: bool,
        interval: float,
    ) -> "MailerData":
        chat_ids = set(chat_ids)
        return MailerData(
            chat_ids=list(chat_ids),
            settings=MailerSettingsData(
                message=message,
                reply_markup=reply_markup,
                disable_notification=disable_notification,
                interval=interval,
                total_chats=len(chat_ids),
            ),
        )

    @classmethod
    def build_from_json(
        cls,
        *,
        chat_ids: List[int],
        settings: str,
    ) -> "MailerData":
        return MailerData(
            chat_ids=chat_ids,
            settings=MailerSettingsData.model_validate_json(settings),
        )


class Statistic(NamedTuple):
    total_chats: int
    success: int
    failed: int
    ratio: float
