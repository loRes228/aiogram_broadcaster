from typing import TYPE_CHECKING, List, Optional, Union

from aiogram.client.default import Default
from aiogram.methods import SendDocument
from aiogram.types import (
    ForceReply,
    InlineKeyboardMarkup,
    InputFile,
    MessageEntity,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from .base import BaseContent


class DocumentContent(BaseContent):
    document: Union[InputFile, str]
    business_connection_id: Optional[str] = None
    thumbnail: Optional[InputFile] = None
    caption: Optional[str] = None
    parse_mode: Optional[Union[str, Default]] = Default("parse_mode")
    caption_entities: Optional[List[MessageEntity]] = None
    disable_content_type_detection: Optional[bool] = None
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

    async def __call__(self, chat_id: int) -> SendDocument:
        return SendDocument(
            chat_id=chat_id,
            document=self.document,
            business_connection_id=self.business_connection_id,
            thumbnail=self.thumbnail,
            caption=self.caption,
            parse_mode=self.parse_mode,
            caption_entities=self.caption_entities,
            disable_content_type_detection=self.disable_content_type_detection,
            disable_notification=self.disable_notification,
            protect_content=self.protect_content,
            reply_markup=self.reply_markup,
        )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            document: Union[InputFile, str],
            business_connection_id: Optional[str] = ...,
            thumbnail: Optional[InputFile] = ...,
            caption: Optional[str] = ...,
            parse_mode: Optional[Union[str, Default]] = ...,
            caption_entities: Optional[List[MessageEntity]] = ...,
            disable_content_type_detection: Optional[bool] = ...,
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
