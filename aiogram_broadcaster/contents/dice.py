from typing import TYPE_CHECKING, Any, Optional, Union

from aiogram.client.default import Default
from aiogram.methods import SendDice, TelegramMethod
from aiogram.types import (
    ForceReply,
    InlineKeyboardMarkup,
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


class DiceContent(BaseContent):
    emoji: Optional[str] = None
    disable_notification: Optional[bool] = None
    protect_content: Optional[Union[bool, Default]] = Default("protect_content")
    reply_markup: ReplyMarkupType = None

    async def as_method(self, chat_id: int, **_: Any) -> TelegramMethod[Any]:
        return SendDice(
            chat_id=chat_id,
            emoji=self.emoji,
            disable_notification=self.disable_notification,
            protect_content=self.protect_content,
            reply_markup=self.reply_markup,
        )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            emoji: Optional[str] = ...,
            disable_notification: Optional[bool] = ...,
            protect_content: Optional[bool] = ...,
            reply_markup: ReplyMarkupType = ...,
        ) -> None: ...
