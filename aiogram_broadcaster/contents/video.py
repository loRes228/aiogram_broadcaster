from typing import TYPE_CHECKING, Any, List, Optional, Union

from aiogram.client.default import Default
from aiogram.methods import SendVideo, TelegramMethod
from aiogram.types import (
    ForceReply,
    InlineKeyboardMarkup,
    MessageEntity,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from .base import BaseContent


class VideoContent(BaseContent):
    video: str
    duration: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    caption: Optional[str] = None
    parse_mode: Optional[Union[str, Default]] = Default("parse_mode")
    caption_entities: Optional[List[MessageEntity]] = None
    has_spoiler: Optional[bool] = None
    supports_streaming: Optional[bool] = None
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

    async def as_method(self, chat_id: int, **_: Any) -> TelegramMethod[Any]:
        return SendVideo(
            chat_id=chat_id,
            video=self.video,
            duration=self.duration,
            width=self.width,
            height=self.height,
            caption=self.caption,
            parse_mode=self.parse_mode,
            caption_entities=self.caption_entities,
            has_spoiler=self.has_spoiler,
            supports_streaming=self.supports_streaming,
            disable_notification=self.disable_notification,
            protect_content=self.protect_content,
            reply_markup=self.reply_markup,
        )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            video: str,
            duration: Optional[int] = ...,
            width: Optional[int] = ...,
            height: Optional[int] = ...,
            caption: Optional[str] = ...,
            parse_mode: Optional[str] = ...,
            caption_entities: Optional[List[MessageEntity]] = ...,
            has_spoiler: Optional[bool] = ...,
            supports_streaming: Optional[bool] = ...,
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
