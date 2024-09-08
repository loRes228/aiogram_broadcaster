# THIS CODE WAS AUTO-GENERATED VIA `butcher`

from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    Union,
)

from aiogram.methods import (
    SendPaidMedia,
)
from aiogram.types import (
    ForceReply,
    InlineKeyboardMarkup,
    InputPaidMediaPhoto,
    InputPaidMediaVideo,
    MessageEntity,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from .base import BaseContent


class PaidMediaContent(BaseContent):
    star_count: int
    media: list[Union[InputPaidMediaPhoto, InputPaidMediaVideo]]
    business_connection_id: Optional[str] = None
    payload: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    caption_entities: Optional[list[MessageEntity]] = None
    show_caption_above_media: Optional[bool] = None
    disable_notification: Optional[bool] = None
    protect_content: Optional[bool] = None
    reply_markup: Optional[
        Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]
    ] = None

    async def __call__(self, chat_id: int) -> SendPaidMedia:
        return SendPaidMedia(
            chat_id=chat_id,
            star_count=self.star_count,
            media=self.media,
            business_connection_id=self.business_connection_id,
            payload=self.payload,
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
            star_count: int,
            media: list[Union[InputPaidMediaPhoto, InputPaidMediaVideo]],
            business_connection_id: Optional[str] = ...,
            payload: Optional[str] = ...,
            caption: Optional[str] = ...,
            parse_mode: Optional[str] = ...,
            caption_entities: Optional[list[MessageEntity]] = ...,
            show_caption_above_media: Optional[bool] = ...,
            disable_notification: Optional[bool] = ...,
            protect_content: Optional[bool] = ...,
            reply_markup: Optional[
                Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]
            ] = ...,
            **kwargs: Any,
        ) -> None: ...
