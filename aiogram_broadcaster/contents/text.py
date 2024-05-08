from typing import TYPE_CHECKING, List, Optional, Union

from aiogram.client.default import Default
from aiogram.methods import SendMessage
from aiogram.types import (
    ForceReply,
    InlineKeyboardMarkup,
    LinkPreviewOptions,
    MessageEntity,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from .base import BaseContent


class TextContent(BaseContent):
    text: str
    business_connection_id: Optional[str] = None
    parse_mode: Optional[Union[str, Default]] = Default("parse_mode")
    entities: Optional[List[MessageEntity]] = None
    link_preview_options: Optional[Union[LinkPreviewOptions, Default]] = Default("link_preview")
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

    async def __call__(self, chat_id: int) -> SendMessage:
        return SendMessage(
            chat_id=chat_id,
            text=self.text,
            business_connection_id=self.business_connection_id,
            parse_mode=self.parse_mode,
            entities=self.entities,
            link_preview_options=self.link_preview_options,
            disable_notification=self.disable_notification,
            protect_content=self.protect_content,
            reply_markup=self.reply_markup,
        )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            text: str,
            business_connection_id: Optional[str] = ...,
            parse_mode: Optional[Union[str, Default]] = ...,
            entities: Optional[List[MessageEntity]] = ...,
            link_preview_options: Optional[Union[LinkPreviewOptions, Default]] = ...,
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
