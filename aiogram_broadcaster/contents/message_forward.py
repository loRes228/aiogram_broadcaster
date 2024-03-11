from typing import TYPE_CHECKING, Any, Optional, Union

from aiogram.client.default import Default
from aiogram.methods import TelegramMethod
from aiogram.types import Message

from .base import BaseContent


class MessageForwardContent(BaseContent):
    message: Message
    disable_notification: Optional[bool] = None
    protect_content: Optional[Union[bool, Default]] = Default("protect_content")

    async def as_method(self, chat_id: int, **_: Any) -> TelegramMethod[Any]:
        return self.message.forward(
            chat_id=chat_id,
            disable_notification=self.disable_notification,
            protect_content=self.protect_content,
        )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            message: Message,
            disable_notification: Optional[bool] = ...,
            protect_content: Optional[bool] = ...,
        ) -> None: ...
