from typing import TYPE_CHECKING, Any, List, Optional, Union

from aiogram.client.default import Default
from aiogram.methods import SendAudio, TelegramMethod
from aiogram.types import (
    ForceReply,
    InlineKeyboardMarkup,
    InputFile,
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


class AudioContent(BaseContent):
    audio: Union[InputFile, str]
    caption: Optional[str] = None
    parse_mode: Optional[Union[str, Default]] = Default("parse_mode")
    caption_entities: Optional[List[MessageEntity]] = None
    duration: Optional[int] = None
    performer: Optional[str] = None
    title: Optional[str] = None
    thumbnail: Optional[InputFile] = None
    disable_notification: Optional[bool] = None
    protect_content: Optional[Union[bool, Default]] = Default("protect_content")
    reply_markup: ReplyMarkupType = None

    async def as_method(self, chat_id: int, **_: Any) -> TelegramMethod[Any]:
        return SendAudio(
            chat_id=chat_id,
            audio=self.audio,
            caption=self.caption,
            parse_mode=self.parse_mode,
            caption_entities=self.caption_entities,
            duration=self.duration,
            performer=self.performer,
            title=self.title,
            thumbnail=self.thumbnail,
            disable_notification=self.disable_notification,
            protect_content=self.protect_content,
            reply_markup=self.reply_markup,
        )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            audio: Union[InputFile, str],
            caption: Optional[str] = ...,
            parse_mode: Optional[str] = ...,
            caption_entities: Optional[List[MessageEntity]] = ...,
            duration: Optional[int] = ...,
            performer: Optional[str] = ...,
            title: Optional[str] = ...,
            thumbnail: Optional[InputFile] = ...,
            disable_notification: Optional[bool] = ...,
            protect_content: Optional[bool] = ...,
            reply_markup: ReplyMarkupType = ...,
        ) -> None: ...
