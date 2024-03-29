from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, List, Optional, Union

from aiogram.client.default import Default
from aiogram.methods import SendPoll, TelegramMethod
from aiogram.types import (
    ForceReply,
    InlineKeyboardMarkup,
    MessageEntity,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from .base import BaseContent


ReplyMarkupType = Optional[
    Union[
        InlineKeyboardMarkup,
        ReplyKeyboardMarkup,
        ReplyKeyboardRemove,
        ForceReply,
    ]
]


class PollContent(BaseContent):
    question: str
    options: List[str]
    is_anonymous: Optional[bool] = None
    type: Optional[str] = None
    allows_multiple_answers: Optional[bool] = None
    correct_option_id: Optional[int] = None
    explanation: Optional[str] = None
    explanation_parse_mode: Optional[Union[str, Default]] = Default("parse_mode")
    explanation_entities: Optional[List[MessageEntity]] = None
    open_period: Optional[int] = None
    close_date: Optional[Union[datetime, timedelta, int]] = None
    is_closed: Optional[bool] = None
    disable_notification: Optional[bool] = None
    protect_content: Optional[Union[bool, Default]] = Default("protect_content")
    reply_markup: ReplyMarkupType = None

    async def as_method(self, chat_id: int, **_: Any) -> TelegramMethod[Any]:
        return SendPoll(
            chat_id=chat_id,
            question=self.question,
            options=self.options,
            is_anonymous=self.is_anonymous,
            type=self.type,
            allows_multiple_answers=self.allows_multiple_answers,
            correct_option_id=self.correct_option_id,
            explanation=self.explanation,
            explanation_parse_mode=self.explanation_parse_mode,
            explanation_entities=self.explanation_entities,
            open_period=self.open_period,
            close_date=self.close_date,
            is_closed=self.is_closed,
            disable_notification=self.disable_notification,
            protect_content=self.protect_content,
            reply_markup=self.reply_markup,
        )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            question: str,
            options: List[str],
            is_anonymous: Optional[bool] = ...,
            type: Optional[str] = ...,  # noqa: A002
            allows_multiple_answers: Optional[bool] = ...,
            correct_option_id: Optional[int] = ...,
            explanation: Optional[str] = ...,
            explanation_parse_mode: Optional[str] = ...,
            explanation_entities: Optional[List[MessageEntity]] = ...,
            open_period: Optional[int] = ...,
            close_date: Optional[Union[datetime, timedelta, int]] = ...,
            is_closed: Optional[bool] = ...,
            disable_notification: Optional[bool] = ...,
            protect_content: Optional[bool] = ...,
            reply_markup: ReplyMarkupType = ...,
        ) -> None: ...
