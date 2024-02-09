from typing import Any, Dict

from aiogram import Bot
from aiogram.types import Message
from typing_extensions import assert_never

from .enums import Strategy
from .settings import MessageSettings


class Messenger:
    bot: Bot
    strategy: Strategy
    settings: MessageSettings

    __slots__ = (
        "bot",
        "settings",
        "strategy",
    )

    def __init__(
        self,
        bot: Bot,
        strategy: Strategy,
        settings: MessageSettings,
    ) -> None:
        self.bot = bot
        self.strategy = strategy
        self.settings = settings

    @property
    def message(self) -> Message:
        return self.settings.message.as_(bot=self.bot)

    async def send(self, chat_id: int) -> Any:
        kwargs: Dict[str, Any] = {
            "chat_id": chat_id,
            "reply_markup": self.settings.reply_markup,
            "disable_notification": self.settings.disable_notification,
            "protect_content": self.settings.protect_content,
        }
        if self.strategy == Strategy.SEND:
            kwargs.pop("protect_content")
            await self.message.send_copy(**kwargs)
        elif self.strategy == Strategy.COPY:
            await self.message.copy_to(**kwargs)
        elif self.strategy == Strategy.FORWARD:
            await self.message.forward(**kwargs)
        else:
            assert_never(self.strategy)
