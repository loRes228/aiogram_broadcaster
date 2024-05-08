from typing import TYPE_CHECKING, List, Optional, Union

from aiogram.client.default import Default
from aiogram.methods import SendMediaGroup
from aiogram.types import InputMediaAudio, InputMediaDocument, InputMediaPhoto, InputMediaVideo

from .base import BaseContent


class MediaGroupContent(BaseContent):
    media: List[
        Union[
            InputMediaAudio,
            InputMediaDocument,
            InputMediaPhoto,
            InputMediaVideo,
        ]
    ]
    business_connection_id: Optional[str] = None
    disable_notification: Optional[bool] = None
    protect_content: Optional[Union[bool, Default]] = Default("protect_content")

    async def __call__(self, chat_id: int) -> SendMediaGroup:
        return SendMediaGroup(
            chat_id=chat_id,
            media=self.media,
            business_connection_id=self.business_connection_id,
            disable_notification=self.disable_notification,
            protect_content=self.protect_content,
        )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            media: List[
                Union[
                    InputMediaAudio,
                    InputMediaDocument,
                    InputMediaPhoto,
                    InputMediaVideo,
                ]
            ],
            business_connection_id: Optional[str] = ...,
            disable_notification: Optional[bool] = ...,
            protect_content: Optional[Union[bool, Default]] = ...,
        ) -> None: ...
