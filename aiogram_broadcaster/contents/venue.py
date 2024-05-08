from typing import TYPE_CHECKING, Optional, Union

from aiogram.client.default import Default
from aiogram.methods import SendVenue
from aiogram.types import (
    ForceReply,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from .base import BaseContent


class VenueContent(BaseContent):
    latitude: float
    longitude: float
    title: str
    address: str
    business_connection_id: Optional[str] = None
    foursquare_id: Optional[str] = None
    foursquare_type: Optional[str] = None
    google_place_id: Optional[str] = None
    google_place_type: Optional[str] = None
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

    async def __call__(self, chat_id: int) -> SendVenue:
        return SendVenue(
            chat_id=chat_id,
            latitude=self.latitude,
            longitude=self.longitude,
            title=self.title,
            address=self.address,
            business_connection_id=self.business_connection_id,
            foursquare_id=self.foursquare_id,
            foursquare_type=self.foursquare_type,
            google_place_id=self.google_place_id,
            google_place_type=self.google_place_type,
            disable_notification=self.disable_notification,
            protect_content=self.protect_content,
            reply_markup=self.reply_markup,
        )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            latitude: float,
            longitude: float,
            title: str,
            address: str,
            business_connection_id: Optional[str] = ...,
            foursquare_id: Optional[str] = ...,
            foursquare_type: Optional[str] = ...,
            google_place_id: Optional[str] = ...,
            google_place_type: Optional[str] = ...,
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
