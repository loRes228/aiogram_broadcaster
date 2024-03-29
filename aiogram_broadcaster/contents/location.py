from typing import TYPE_CHECKING, Any, Optional, Union

from aiogram.client.default import Default
from aiogram.methods import SendLocation, TelegramMethod
from aiogram.types import (
    ForceReply,
    InlineKeyboardMarkup,
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


class LocationContent(BaseContent):
    latitude: float
    longitude: float
    horizontal_accuracy: Optional[float] = None
    live_period: Optional[int] = None
    heading: Optional[int] = None
    proximity_alert_radius: Optional[int] = None
    disable_notification: Optional[bool] = None
    protect_content: Optional[Union[bool, Default]] = Default("protect_content")
    reply_markup: ReplyMarkupType = None

    async def as_method(self, chat_id: int, **_: Any) -> TelegramMethod[Any]:
        return SendLocation(
            chat_id=chat_id,
            latitude=self.latitude,
            longitude=self.longitude,
            horizontal_accuracy=self.horizontal_accuracy,
            live_period=self.live_period,
            heading=self.heading,
            proximity_alert_radius=self.proximity_alert_radius,
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
            horizontal_accuracy: Optional[float] = ...,
            live_period: Optional[int] = ...,
            heading: Optional[int] = ...,
            proximity_alert_radius: Optional[int] = ...,
            disable_notification: Optional[bool] = ...,
            protect_content: Optional[bool] = ...,
            reply_markup: ReplyMarkupType = ...,
        ) -> None: ...
