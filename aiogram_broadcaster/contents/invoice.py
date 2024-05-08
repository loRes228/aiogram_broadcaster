from typing import TYPE_CHECKING, List, Optional, Union

from aiogram.client.default import Default
from aiogram.methods import SendInvoice
from aiogram.types import (
    InlineKeyboardMarkup,
    LabeledPrice,
)

from .base import BaseContent


class InvoiceContent(BaseContent):
    title: str
    description: str
    payload: str
    provider_token: str
    currency: str
    prices: List[LabeledPrice]
    max_tip_amount: Optional[int] = None
    suggested_tip_amounts: Optional[List[int]] = None
    start_parameter: Optional[str] = None
    provider_data: Optional[str] = None
    photo_url: Optional[str] = None
    photo_size: Optional[int] = None
    photo_width: Optional[int] = None
    photo_height: Optional[int] = None
    need_name: Optional[bool] = None
    need_phone_number: Optional[bool] = None
    need_email: Optional[bool] = None
    need_shipping_address: Optional[bool] = None
    send_phone_number_to_provider: Optional[bool] = None
    send_email_to_provider: Optional[bool] = None
    is_flexible: Optional[bool] = None
    disable_notification: Optional[bool] = None
    protect_content: Optional[Union[bool, Default]] = Default("protect_content")
    reply_markup: Optional[InlineKeyboardMarkup] = None

    async def __call__(self, chat_id: int) -> SendInvoice:
        return SendInvoice(
            chat_id=chat_id,
            title=self.title,
            description=self.description,
            payload=self.payload,
            provider_token=self.provider_token,
            currency=self.currency,
            prices=self.prices,
            max_tip_amount=self.max_tip_amount,
            suggested_tip_amounts=self.suggested_tip_amounts,
            start_parameter=self.start_parameter,
            provider_data=self.provider_data,
            photo_url=self.photo_url,
            photo_size=self.photo_size,
            photo_width=self.photo_width,
            photo_height=self.photo_height,
            need_name=self.need_name,
            need_phone_number=self.need_phone_number,
            need_email=self.need_email,
            need_shipping_address=self.need_shipping_address,
            send_phone_number_to_provider=self.send_phone_number_to_provider,
            send_email_to_provider=self.send_email_to_provider,
            is_flexible=self.is_flexible,
            disable_notification=self.disable_notification,
            protect_content=self.protect_content,
            reply_markup=self.reply_markup,
        )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            title: str,
            description: str,
            payload: str,
            provider_token: str,
            currency: str,
            prices: List[LabeledPrice],
            max_tip_amount: Optional[int] = ...,
            suggested_tip_amounts: Optional[List[int]] = ...,
            start_parameter: Optional[str] = ...,
            provider_data: Optional[str] = ...,
            photo_url: Optional[str] = ...,
            photo_size: Optional[int] = ...,
            photo_width: Optional[int] = ...,
            photo_height: Optional[int] = ...,
            need_name: Optional[bool] = ...,
            need_phone_number: Optional[bool] = ...,
            need_email: Optional[bool] = ...,
            need_shipping_address: Optional[bool] = ...,
            send_phone_number_to_provider: Optional[bool] = ...,
            send_email_to_provider: Optional[bool] = ...,
            is_flexible: Optional[bool] = ...,
            disable_notification: Optional[bool] = ...,
            protect_content: Optional[Union[bool, Default]] = ...,
            reply_markup: Optional[InlineKeyboardMarkup] = ...,
        ) -> None: ...
