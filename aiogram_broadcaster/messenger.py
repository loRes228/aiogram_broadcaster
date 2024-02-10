from typing import Any

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

    async def send(self, chat_id: int) -> Message:
        return await self.strategy_send(
            chat_id=chat_id,
            reply_markup=self.settings.reply_markup,
            disable_notification=self.settings.disable_notification,
            protect_content=self.settings.protect_content,
        )

    async def strategy_send(self, **kwargs: Any) -> Message:
        if self.strategy == Strategy.SEND:
            kwargs.pop("protect_content")
            return await self.message.send_copy(**kwargs)
        if self.strategy == Strategy.COPY:
            await self.message.copy_to(**kwargs)
            return self.message
        if self.strategy == Strategy.FORWARD:
            return await self.message.forward(**kwargs)
        assert_never(self.strategy)
