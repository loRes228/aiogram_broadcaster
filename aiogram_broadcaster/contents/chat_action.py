from typing import TYPE_CHECKING, Optional

from aiogram.methods import SendChatAction

from .base import BaseContent


class ChatActionContent(BaseContent):
    action: str
    business_connection_id: Optional[str] = None

    async def __call__(self, chat_id: int) -> SendChatAction:
        return SendChatAction(
            chat_id=chat_id,
            action=self.action,
            business_connection_id=self.business_connection_id,
        )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            action: str,
            business_connection_id: Optional[str] = ...,
        ) -> None: ...
