from typing import TYPE_CHECKING, Any, List, Optional, Union

from aiogram.client.default import Default
from aiogram.methods import SendMediaGroup, TelegramMethod
from aiogram.types import (
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
)

from aiogram_broadcaster.contents import BaseContent


class MediaGroupContent(BaseContent):
    media: List[
        Union[
            InputMediaAudio,
            InputMediaDocument,
            InputMediaPhoto,
            InputMediaVideo,
        ]
    ]
    disable_notification: Optional[bool] = None
    protect_content: Optional[Union[bool, Default]] = Default("protect_content")

    async def as_method(self, chat_id: int, **_: Any) -> TelegramMethod[Any]:
        return SendMediaGroup(
            chat_id=chat_id,
            media=self.media,
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
            disable_notification: Optional[bool] = ...,
            protect_content: Optional[bool] = ...,
        ) -> None: ...
