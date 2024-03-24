from typing import TYPE_CHECKING, Any, List, Optional, Union

from aiogram.client.default import Default
from aiogram.methods import SendMessage, TelegramMethod
from aiogram.types import (
    ForceReply,
    InlineKeyboardMarkup,
    LinkPreviewOptions,
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


class TextContent(BaseContent):
    text: str
    parse_mode: Optional[Union[str, Default]] = Default("parse_mode")
    entities: Optional[List[MessageEntity]] = None
    link_preview_options: Optional[Union[LinkPreviewOptions, Default]] = Default("link_preview")
    disable_notification: Optional[bool] = None
    protect_content: Optional[Union[bool, Default]] = Default("protect_content")
    reply_markup: ReplyMarkupType = None

    async def as_method(self, chat_id: int, **_: Any) -> TelegramMethod[Any]:
        return SendMessage(
            chat_id=chat_id,
            text=self.text,
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
            parse_mode: Optional[str] = ...,
            entities: Optional[List[MessageEntity]] = ...,
            link_preview_options: Optional[LinkPreviewOptions] = ...,
            disable_notification: Optional[bool] = ...,
            protect_content: Optional[bool] = ...,
            reply_markup: ReplyMarkupType = ...,
        ) -> None: ...
