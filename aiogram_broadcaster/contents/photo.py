# THIS CODE WAS AUTO-GENERATED VIA `butcher`

from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    Union,
)

from aiogram.client.default import Default
from aiogram.methods import (
    SendPhoto,
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


class PhotoContent(BaseContent):
    photo: Union[str, InputFile]
    business_connection_id: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[Union[str, Default]] = Default("parse_mode")
    caption_entities: Optional[list[MessageEntity]] = None
    show_caption_above_media: Optional[Union[bool, Default]] = Default("show_caption_above_media")
    has_spoiler: Optional[bool] = None
    disable_notification: Optional[bool] = None
    protect_content: Optional[Union[bool, Default]] = Default("protect_content")
    allow_paid_broadcast: Optional[bool] = None
    message_effect_id: Optional[str] = None
    suggested_post_parameters: Optional[SuggestedPostParameters] = None
    reply_markup: Optional[
        Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]
    ] = None

    async def __call__(self, chat_id: int) -> SendPhoto:
        return SendPhoto(
            chat_id=chat_id,
            photo=self.photo,
            business_connection_id=self.business_connection_id,
            caption=self.caption,
            parse_mode=self.parse_mode,
            caption_entities=self.caption_entities,
            show_caption_above_media=self.show_caption_above_media,
            has_spoiler=self.has_spoiler,
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
            photo: Union[str, InputFile],
            business_connection_id: Optional[str] = ...,
            caption: Optional[str] = ...,
            parse_mode: Optional[Union[str, Default]] = ...,
            caption_entities: Optional[list[MessageEntity]] = ...,
            show_caption_above_media: Optional[Union[bool, Default]] = ...,
            has_spoiler: Optional[bool] = ...,
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
