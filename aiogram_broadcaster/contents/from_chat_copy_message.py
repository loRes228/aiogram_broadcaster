# THIS CODE WAS AUTO-GENERATED VIA `butcher`

from datetime import datetime, timedelta
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    Union,
)

from aiogram.client.default import Default
from aiogram.methods import (
    CopyMessage,
)
from aiogram.types import (
    ForceReply,
    InlineKeyboardMarkup,
    MessageEntity,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from .base import BaseContent


class FromChatCopyMessageContent(BaseContent):
    from_chat_id: Union[int, str]
    message_id: int
    video_start_timestamp: Optional[Union[datetime, timedelta, int]] = None
    caption: Optional[str] = None
    parse_mode: Optional[Union[str, Default]] = Default("parse_mode")
    caption_entities: Optional[list[MessageEntity]] = None
    show_caption_above_media: Optional[Union[bool, Default]] = Default("show_caption_above_media")
    disable_notification: Optional[bool] = None
    protect_content: Optional[Union[bool, Default]] = Default("protect_content")
    reply_markup: Optional[
        Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]
    ] = None

    async def __call__(self, chat_id: int) -> CopyMessage:
        return CopyMessage(
            chat_id=chat_id,
            from_chat_id=self.from_chat_id,
            message_id=self.message_id,
            video_start_timestamp=self.video_start_timestamp,
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
            from_chat_id: Union[int, str],
            message_id: int,
            video_start_timestamp: Optional[Union[datetime, timedelta, int]] = ...,
            caption: Optional[str] = ...,
            parse_mode: Optional[Union[str, Default]] = ...,
            caption_entities: Optional[list[MessageEntity]] = ...,
            show_caption_above_media: Optional[Union[bool, Default]] = ...,
            disable_notification: Optional[bool] = ...,
            protect_content: Optional[Union[bool, Default]] = ...,
            reply_markup: Optional[
                Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]
            ] = ...,
            **kwargs: Any,
        ) -> None: ...
