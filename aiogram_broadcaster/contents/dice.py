# THIS CODE WAS AUTO-GENERATED VIA `butcher`

from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    Union,
)

from aiogram.client.default import Default
from aiogram.methods import (
    SendDice,
)
from aiogram.types import (
    ForceReply,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    SuggestedPostParameters,
)

from .base import BaseContent


class DiceContent(BaseContent):
    business_connection_id: Optional[str] = None
    emoji: Optional[str] = None
    disable_notification: Optional[bool] = None
    protect_content: Optional[Union[bool, Default]] = Default("protect_content")
    allow_paid_broadcast: Optional[bool] = None
    message_effect_id: Optional[str] = None
    suggested_post_parameters: Optional[SuggestedPostParameters] = None
    reply_markup: Optional[
        Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]
    ] = None

    async def __call__(self, chat_id: int) -> SendDice:
        return SendDice(
            chat_id=chat_id,
            business_connection_id=self.business_connection_id,
            emoji=self.emoji,
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
            business_connection_id: Optional[str] = ...,
            emoji: Optional[str] = ...,
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
