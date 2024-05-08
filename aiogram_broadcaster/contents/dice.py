from typing import TYPE_CHECKING, Optional, Union

from aiogram.client.default import Default
from aiogram.methods import SendDice
from aiogram.types import (
    ForceReply,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from .base import BaseContent


class DiceContent(BaseContent):
    business_connection_id: Optional[str] = None
    emoji: Optional[str] = None
    disable_notification: Optional[bool] = None
    protect_content: Optional[Union[bool, Default]] = Default("protect_content")
    reply_markup: Optional[
        Union[
            InlineKeyboardMarkup,
            ReplyKeyboardMarkup,
            ReplyKeyboardRemove,
            ForceReply,
        ]
    ] = None

    async def __call__(self, chat_id: int) -> SendDice:
        return SendDice(
            chat_id=chat_id,
            business_connection_id=self.business_connection_id,
            emoji=self.emoji,
            disable_notification=self.disable_notification,
            protect_content=self.protect_content,
            reply_markup=self.reply_markup,
        )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            business_connection_id: Optional[str] = ...,
            emoji: Optional[str] = ...,
            disable_notification: Optional[bool] = ...,
            protect_content: Optional[Union[bool, Default]] = ...,
            reply_markup: Optional[
                Union[
                    InlineKeyboardMarkup,
                    ReplyKeyboardMarkup,
                    ReplyKeyboardRemove,
                    ForceReply,
                ]
            ] = ...,
        ) -> None: ...
