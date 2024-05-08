from typing import TYPE_CHECKING, Optional, Union

from aiogram.client.default import Default
from aiogram.methods import SendVideoNote
from aiogram.types import (
    ForceReply,
    InlineKeyboardMarkup,
    InputFile,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from .base import BaseContent


class VideoNoteContent(BaseContent):
    video_note: Union[InputFile, str]
    business_connection_id: Optional[str] = None
    duration: Optional[int] = None
    length: Optional[int] = None
    thumbnail: Optional[InputFile] = None
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

    async def __call__(self, chat_id: int) -> SendVideoNote:
        return SendVideoNote(
            chat_id=chat_id,
            video_note=self.video_note,
            business_connection_id=self.business_connection_id,
            duration=self.duration,
            length=self.length,
            thumbnail=self.thumbnail,
            disable_notification=self.disable_notification,
            protect_content=self.protect_content,
            reply_markup=self.reply_markup,
        )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            video_note: Union[InputFile, str],
            business_connection_id: Optional[str] = ...,
            duration: Optional[int] = ...,
            length: Optional[int] = ...,
            thumbnail: Optional[InputFile] = ...,
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
