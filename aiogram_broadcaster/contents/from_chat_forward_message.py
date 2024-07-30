# THIS CODE WAS AUTO-GENERATED VIA `butcher`

from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    Union,
)

from aiogram.client.default import Default
from aiogram.methods import (
    ForwardMessage,
)

from .base import BaseContent


class FromChatForwardMessageContent(BaseContent):
    from_chat_id: Union[int, str]
    message_id: int
    disable_notification: Optional[bool] = None
    protect_content: Optional[Union[bool, Default]] = Default("protect_content")

    async def __call__(self, chat_id: int) -> ForwardMessage:
        return ForwardMessage(
            chat_id=chat_id,
            from_chat_id=self.from_chat_id,
            message_id=self.message_id,
            disable_notification=self.disable_notification,
            protect_content=self.protect_content,
            **(self.model_extra or {}),
        )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            from_chat_id: Union[int, str],
            message_id: int,
            disable_notification: Optional[bool] = ...,
            protect_content: Optional[Union[bool, Default]] = ...,
            **kwargs: Any,
        ) -> None: ...
