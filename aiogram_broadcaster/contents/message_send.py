# THIS CODE WAS AUTO-GENERATED VIA `butcher`

from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    Union,
)

from aiogram.methods import (
    ForwardMessage,
    SendAnimation,
    SendAudio,
    SendContact,
    SendDice,
    SendDocument,
    SendLocation,
    SendMessage,
    SendPhoto,
    SendPoll,
    SendSticker,
    SendVenue,
    SendVideo,
    SendVideoNote,
    SendVoice,
)
from aiogram.types import (
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
)

from .base import BaseContent


class MessageSendContent(BaseContent):
    message: Message
    disable_notification: Optional[bool] = None
    reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]] = None
    business_connection_id: Optional[str] = None
    parse_mode: Optional[str] = None
    message_effect_id: Optional[str] = None

    async def __call__(
        self,
        chat_id: int,
    ) -> Union[
        ForwardMessage,
        SendAnimation,
        SendAudio,
        SendContact,
        SendDocument,
        SendLocation,
        SendMessage,
        SendPhoto,
        SendPoll,
        SendDice,
        SendSticker,
        SendVenue,
        SendVideo,
        SendVideoNote,
        SendVoice,
    ]:
        return self.message.send_copy(
            chat_id=chat_id,
            disable_notification=self.disable_notification,
            reply_markup=self.reply_markup,
            business_connection_id=self.business_connection_id,
            parse_mode=self.parse_mode,
            message_effect_id=self.message_effect_id,
        )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            message: Message,
            disable_notification: Optional[bool] = ...,
            reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]] = ...,
            business_connection_id: Optional[str] = ...,
            parse_mode: Optional[str] = ...,
            message_effect_id: Optional[str] = ...,
            **kwargs: Any,
        ) -> None: ...
