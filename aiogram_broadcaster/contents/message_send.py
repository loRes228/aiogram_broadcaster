from typing import TYPE_CHECKING, Any, Optional, Union

from aiogram.methods import TelegramMethod
from aiogram.types import InlineKeyboardMarkup, Message, ReplyKeyboardMarkup

from .base import BaseContent


ReplyMarkupType = Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]]


class MessageSendContent(BaseContent):
    message: Message
    disable_notification: Optional[bool] = None
    reply_markup: ReplyMarkupType = None
    parse_mode: Optional[str] = None

    async def __call__(self, chat_id: int) -> TelegramMethod[Any]:
        return self.message.send_copy(
            chat_id=chat_id,
            disable_notification=self.disable_notification,
            reply_markup=self.reply_markup,
            parse_mode=self.parse_mode,
        )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            message: Message,
            disable_notification: Optional[bool] = ...,
            reply_markup: ReplyMarkupType = ...,
            parse_mode: Optional[str] = ...,
        ) -> None: ...
