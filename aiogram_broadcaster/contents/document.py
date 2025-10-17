# THIS CODE WAS AUTO-GENERATED VIA `butcher`

from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    Union,
)

from aiogram.client.default import Default
from aiogram.methods import (
    SendDocument,
)
from aiogram.types import (
    ForceReply,
    InlineKeyboardMarkup,
    InputFile,
    MessageEntity,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    SuggestedPostParameters,
)

from .base import BaseContent


class DocumentContent(BaseContent):
    document: Union[str, InputFile]
    business_connection_id: Optional[str] = None
    thumbnail: Optional[InputFile] = None
    caption: Optional[str] = None
    parse_mode: Optional[Union[str, Default]] = Default("parse_mode")
    caption_entities: Optional[list[MessageEntity]] = None
    disable_content_type_detection: Optional[bool] = None
    disable_notification: Optional[bool] = None
    protect_content: Optional[Union[bool, Default]] = Default("protect_content")
    allow_paid_broadcast: Optional[bool] = None
    message_effect_id: Optional[str] = None
    suggested_post_parameters: Optional[SuggestedPostParameters] = None
    reply_markup: Optional[
        Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]
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
            allow_paid_broadcast=self.allow_paid_broadcast,
            message_effect_id=self.message_effect_id,
            suggested_post_parameters=self.suggested_post_parameters,
            reply_markup=self.reply_markup,
            **(self.model_extra or {}),
        )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            document: Union[str, InputFile],
            business_connection_id: Optional[str] = ...,
            thumbnail: Optional[InputFile] = ...,
            caption: Optional[str] = ...,
            parse_mode: Optional[Union[str, Default]] = ...,
            caption_entities: Optional[list[MessageEntity]] = ...,
            disable_content_type_detection: Optional[bool] = ...,
            disable_notification: Optional[bool] = ...,
            protect_content: Optional[Union[bool, Default]] = ...,
            allow_paid_broadcast: Optional[bool] = ...,
            message_effect_id: Optional[str] = ...,
            suggested_post_parameters: Optional[SuggestedPostParameters] = ...,
            reply_markup: Optional[
                Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]
            ] = ...,
            **kwargs: Any,
        ) -> None: ...
