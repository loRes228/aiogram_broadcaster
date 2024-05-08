from typing import TYPE_CHECKING, Optional, Union

from aiogram.client.default import Default
from aiogram.methods import SendGame
from aiogram.types import (
    InlineKeyboardMarkup,
)

from .base import BaseContent


class GameContent(BaseContent):
    game_short_name: str
    business_connection_id: Optional[str] = None
    disable_notification: Optional[bool] = None
    protect_content: Optional[Union[bool, Default]] = Default("protect_content")
    reply_markup: Optional[InlineKeyboardMarkup] = None

    async def __call__(self, chat_id: int) -> SendGame:
        return SendGame(
            chat_id=chat_id,
            game_short_name=self.game_short_name,
            business_connection_id=self.business_connection_id,
            disable_notification=self.disable_notification,
            protect_content=self.protect_content,
            reply_markup=self.reply_markup,
        )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            game_short_name: str,
            business_connection_id: Optional[str] = ...,
            disable_notification: Optional[bool] = ...,
            protect_content: Optional[Union[bool, Default]] = ...,
            reply_markup: Optional[InlineKeyboardMarkup] = ...,
        ) -> None: ...
