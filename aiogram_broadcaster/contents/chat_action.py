from typing import TYPE_CHECKING

from aiogram.methods import SendChatAction

from .base import BaseContent


class ChatActionContent(BaseContent):
    action: str

    async def __call__(self, chat_id: int) -> SendChatAction:
        return SendChatAction(
            chat_id=chat_id,
            action=self.action,
        )

    if TYPE_CHECKING:

        def __init__(self, *, action: str) -> None: ...
