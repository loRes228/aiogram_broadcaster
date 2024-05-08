from typing import TYPE_CHECKING, List, Optional, Union

from aiogram.client.default import Default
from aiogram.methods import SendAnimation
from aiogram.types import (
    ForceReply,
    InlineKeyboardMarkup,
    InputFile,
    MessageEntity,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from .base import BaseContent


class AnimationContent(BaseContent):
    animation: Union[InputFile, str]
    business_connection_id: Optional[str] = None
    duration: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    thumbnail: Optional[InputFile] = None
    caption: Optional[str] = None
    parse_mode: Optional[Union[str, Default]] = Default("parse_mode")
    caption_entities: Optional[List[MessageEntity]] = None
    has_spoiler: Optional[bool] = None
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

    async def __call__(self, chat_id: int) -> SendAnimation:
        return SendAnimation(
            chat_id=chat_id,
            animation=self.animation,
            business_connection_id=self.business_connection_id,
            duration=self.duration,
            width=self.width,
            height=self.height,
            thumbnail=self.thumbnail,
            caption=self.caption,
            parse_mode=self.parse_mode,
            caption_entities=self.caption_entities,
            has_spoiler=self.has_spoiler,
            disable_notification=self.disable_notification,
            protect_content=self.protect_content,
            reply_markup=self.reply_markup,
        )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            animation: Union[InputFile, str],
            business_connection_id: Optional[str] = ...,
            duration: Optional[int] = ...,
            width: Optional[int] = ...,
            height: Optional[int] = ...,
            thumbnail: Optional[InputFile] = ...,
            caption: Optional[str] = ...,
            parse_mode: Optional[Union[str, Default]] = ...,
            caption_entities: Optional[List[MessageEntity]] = ...,
            has_spoiler: Optional[bool] = ...,
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
