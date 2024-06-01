from typing import TYPE_CHECKING, Any, List, Optional, Union

from aiogram.client.default import Default
from aiogram.methods import (
    CopyMessage,
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
    ForceReply,
    InlineKeyboardMarkup,
    Message,
    MessageEntity,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from .base import BaseContent


class MessageCopyContent(BaseContent):
    message: Message
    caption: Optional[str] = None
    parse_mode: Optional[Union[str, Default]] = Default("parse_mode")
    caption_entities: Optional[List[MessageEntity]] = None
    show_caption_above_media: Optional[Union[bool, Default]] = Default("show_caption_above_media")
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

    async def __call__(self, chat_id: int) -> CopyMessage:
        return self.message.copy_to(
            chat_id=chat_id,
            caption=self.caption,
            parse_mode=self.parse_mode,
            caption_entities=self.caption_entities,
            show_caption_above_media=self.show_caption_above_media,
            disable_notification=self.disable_notification,
            protect_content=self.protect_content,
            reply_markup=self.reply_markup,
            **(self.model_extra or {}),
        )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            message: Message,
            caption: Optional[str] = ...,
            parse_mode: Optional[Union[str, Default]] = ...,
            caption_entities: Optional[List[MessageEntity]] = ...,
            show_caption_above_media: Optional[Union[bool, Default]] = ...,
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
            **kwargs: Any,
        ) -> None: ...


class MessageForwardContent(BaseContent):
    message: Message
    disable_notification: Optional[bool] = None
    protect_content: Optional[Union[bool, Default]] = Default("protect_content")

    async def __call__(self, chat_id: int) -> ForwardMessage:
        return self.message.forward(
            chat_id=chat_id,
            disable_notification=self.disable_notification,
            protect_content=self.protect_content,
            **(self.model_extra or {}),
        )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            message: Message,
            disable_notification: Optional[bool] = ...,
            protect_content: Optional[Union[bool, Default]] = ...,
            **kwargs: Any,
        ) -> None: ...


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
