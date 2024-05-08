from typing import TYPE_CHECKING, List, Optional, Union

from aiogram.client.default import Default
from aiogram.methods import CopyMessage, ForwardMessage
from aiogram.types import (
    ForceReply,
    InlineKeyboardMarkup,
    MessageEntity,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from .base import BaseContent


class FromChatCopyContent(BaseContent):
    from_chat_id: Union[int, str]
    message_id: int
    caption: Optional[str] = None
    parse_mode: Optional[Union[str, Default]] = Default("parse_mode")
    caption_entities: Optional[List[MessageEntity]] = None
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
        return CopyMessage(
            chat_id=chat_id,
            from_chat_id=self.from_chat_id,
            message_id=self.message_id,
            caption=self.caption,
            parse_mode=self.parse_mode,
            caption_entities=self.caption_entities,
            disable_notification=self.disable_notification,
            protect_content=self.protect_content,
            reply_markup=self.reply_markup,
        )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            from_chat_id: Union[int, str],
            message_id: int,
            caption: Optional[str] = ...,
            parse_mode: Optional[str] = ...,
            caption_entities: Optional[List[MessageEntity]] = ...,
            disable_notification: Optional[bool] = ...,
            protect_content: Optional[bool] = ...,
            reply_markup: Optional[
                Union[
                    InlineKeyboardMarkup,
                    ReplyKeyboardMarkup,
                    ReplyKeyboardRemove,
                    ForceReply,
                ]
            ] = ...,
        ) -> None: ...


class FromChatForwardContent(BaseContent):
    from_chat_id: Union[int, str]
    message_id: int
    disable_notification: Optional[bool] = None
    protect_content: Optional[Union[bool, Default]] = Default("protect_content")

    async def __call__(self, chat_id: int) -> ForwardMessage:
        return ForwardMessage(
            chat_id=chat_id,
            from_chat_id=self.from_chat_id,
            message_id=self.message_id,
            disable_notification=self.disable_notification,
            protect_content=self.protect_content,
        )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            from_chat_id: Union[int, str],
            message_id: int,
            disable_notification: Optional[bool] = ...,
            protect_content: Optional[Union[bool, Default]] = ...,
        ) -> None: ...
