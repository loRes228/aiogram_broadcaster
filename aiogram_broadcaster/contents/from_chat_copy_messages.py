# THIS CODE WAS AUTO-GENERATED VIA `butcher`

from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    Union,
)

from aiogram.methods import (
    CopyMessages,
)

from .base import BaseContent


class FromChatCopyMessagesContent(BaseContent):
    from_chat_id: Union[int, str]
    message_ids: list[int]
    disable_notification: Optional[bool] = None
    protect_content: Optional[bool] = None
    remove_caption: Optional[bool] = None

    async def __call__(self, chat_id: int) -> CopyMessages:
        return CopyMessages(
            chat_id=chat_id,
            from_chat_id=self.from_chat_id,
            message_ids=self.message_ids,
            disable_notification=self.disable_notification,
            protect_content=self.protect_content,
            remove_caption=self.remove_caption,
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
            remove_caption: Optional[bool] = ...,
            **kwargs: Any,
        ) -> None: ...
