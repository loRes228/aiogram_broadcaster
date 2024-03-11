from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, NamedTuple


if TYPE_CHECKING:
    from typing import Set

    from aiogram_broadcaster.contents import BaseContent
    from aiogram_broadcaster.mailer.chat_manager import ChatManager, ChatState
    from aiogram_broadcaster.mailer.settings import MailerSettings


class DataComposer(NamedTuple):
    content: BaseContent
    chat_manager: ChatManager
    settings: MailerSettings
    bot_id: int


class BaseBCRStorage(ABC):
    async def get_data(self, mailer_id: int) -> DataComposer:
        content = await self.get_content(mailer_id=mailer_id)
        chat_manager = await self.get_chats(mailer_id=mailer_id)
        settings = await self.get_settings(mailer_id=mailer_id)
        bot_id = await self.get_bot(mailer_id=mailer_id)
        return DataComposer(
            content=content,
            chat_manager=chat_manager,
            settings=settings,
            bot_id=bot_id,
        )

    async def set_data(self, mailer_id: int, data: DataComposer) -> None:
        await self.set_content(mailer_id=mailer_id, content=data.content)
        await self.set_chats(mailer_id=mailer_id, chats=data.chat_manager)
        await self.set_settings(mailer_id=mailer_id, settings=data.settings)
        await self.set_bot(mailer_id=mailer_id, bot=data.bot_id)

    @abstractmethod
    async def get_mailer_ids(self) -> Set[int]:
        pass

    @abstractmethod
    async def delete(self, mailer_id: int) -> None:
        pass

    @abstractmethod
    async def migrate_keys(self, old_mailer_id: int, new_mailer_id: int) -> None:
        pass

    @abstractmethod
    async def get_content(self, mailer_id: int) -> BaseContent:
        pass

    @abstractmethod
    async def set_content(self, mailer_id: int, content: BaseContent) -> None:
        pass

    @abstractmethod
    async def get_chats(self, mailer_id: int) -> ChatManager:
        pass

    @abstractmethod
    async def set_chats(self, mailer_id: int, chats: ChatManager) -> None:
        pass

    @abstractmethod
    async def set_chat_state(self, mailer_id: int, chat: int, state: ChatState) -> None:
        pass

    @abstractmethod
    async def get_settings(self, mailer_id: int) -> MailerSettings:
        pass

    @abstractmethod
    async def set_settings(self, mailer_id: int, settings: MailerSettings) -> None:
        pass

    @abstractmethod
    async def get_bot(self, mailer_id: int) -> int:
        pass

    @abstractmethod
    async def set_bot(self, mailer_id: int, bot: int) -> None:
        pass
