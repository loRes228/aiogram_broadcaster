# THIS CODE WAS AUTO-GENERATED VIA `butcher`

from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    Union,
)

from aiogram.methods import (
    ForwardMessages,
)

from .base import BaseContent


class FromChatForwardMessagesContent(BaseContent):
    from_chat_id: Union[int, str]
    message_ids: list[int]
    disable_notification: Optional[bool] = None
    protect_content: Optional[bool] = None

    async def __call__(self, chat_id: int) -> ForwardMessages:
        return ForwardMessages(
            chat_id=chat_id,
            from_chat_id=self.from_chat_id,
            message_ids=self.message_ids,
            disable_notification=self.disable_notification,
            protect_content=self.protect_content,
            **(self.model_extra or {}),
        )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            from_chat_id: Union[int, str],
            message_ids: list[int],
            disable_notification: Optional[bool] = ...,
            protect_content: Optional[bool] = ...,
            **kwargs: Any,
        ) -> None: ...
