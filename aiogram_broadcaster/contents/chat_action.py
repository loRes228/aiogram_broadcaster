from typing import TYPE_CHECKING, Any

from aiogram.methods import SendChatAction, TelegramMethod

from .base import BaseContent


class ChatActionContent(BaseContent):
    action: str

    async def as_method(self, chat_id: int, **_: Any) -> TelegramMethod[Any]:
        return SendChatAction(
            chat_id=chat_id,
            action=self.action,
        )

    if TYPE_CHECKING:

        def __init__(self, *, action: str) -> None: ...
