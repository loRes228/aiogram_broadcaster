from abc import ABC, abstractmethod
from typing import Tuple

from aiogram_broadcaster.chat_manager import ChatState
from aiogram_broadcaster.settings import (
    ChatsSettings,
    MailerSettings,
    MessageSettings,
    Settings,
)


class BaseMailerStorage(ABC):
    async def get_settings(self, mailer_id: int) -> Settings:
        return Settings(
            chats=await self.get_chats_settings(mailer_id=mailer_id),
            mailer=await self.get_mailer_settings(mailer_id=mailer_id),
            message=await self.get_message_settings(mailer_id=mailer_id),
        )

    async def set_settings(self, mailer_id: int, settings: Settings) -> None:
        await self.set_chats_settings(
            mailer_id=mailer_id,
            settings=settings.chats,
        )
        await self.set_mailer_settings(
            mailer_id=mailer_id,
            settings=settings.mailer,
        )
        await self.set_message_settings(
            mailer_id=mailer_id,
            settings=settings.message,
        )

    @abstractmethod
    async def get_mailer_ids(self) -> Tuple[int, ...]:
        pass

    @abstractmethod
    async def delete_settings(self, mailer_id: int) -> None:
        pass

    @abstractmethod
    async def get_chats_settings(self, mailer_id: int) -> ChatsSettings:
        pass

    @abstractmethod
    async def get_mailer_settings(self, mailer_id: int) -> MailerSettings:
        pass

    @abstractmethod
    async def get_message_settings(self, mailer_id: int) -> MessageSettings:
        pass

    @abstractmethod
    async def set_chats_settings(self, mailer_id: int, settings: ChatsSettings) -> None:
        pass

    @abstractmethod
    async def set_mailer_settings(self, mailer_id: int, settings: MailerSettings) -> None:
        pass

    @abstractmethod
    async def set_message_settings(self, mailer_id: int, settings: MessageSettings) -> None:
        pass

    @abstractmethod
    async def set_chat_state(self, mailer_id: int, chat: int, state: ChatState) -> None:
        pass
