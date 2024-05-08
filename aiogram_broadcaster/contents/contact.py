from typing import TYPE_CHECKING, Optional, Union

from aiogram.client.default import Default
from aiogram.methods import SendContact
from aiogram.types import (
    ForceReply,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from .base import BaseContent


class ContactContent(BaseContent):
    phone_number: str
    first_name: str
    business_connection_id: Optional[str] = None
    last_name: Optional[str] = None
    vcard: Optional[str] = None
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

    async def __call__(self, chat_id: int) -> SendContact:
        return SendContact(
            chat_id=chat_id,
            phone_number=self.phone_number,
            first_name=self.first_name,
            business_connection_id=self.business_connection_id,
            last_name=self.last_name,
            vcard=self.vcard,
            disable_notification=self.disable_notification,
            protect_content=self.protect_content,
            reply_markup=self.reply_markup,
        )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            phone_number: str,
            first_name: str,
            business_connection_id: Optional[str] = ...,
            last_name: Optional[str] = ...,
            vcard: Optional[str] = ...,
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
