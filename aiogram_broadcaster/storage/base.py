from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import Set

    from aiogram_broadcaster.contents import BaseContent
    from aiogram_broadcaster.mailer.chat_engine import ChatEngine, ChatState
    from aiogram_broadcaster.mailer.settings import MailerSettings


class BaseBCRStorage(ABC):
    @abstractmethod
    async def get_mailer_ids(self) -> Set[int]:
        pass

    @abstractmethod
    async def delete(self, mailer_id: int) -> None:
        pass

    @abstractmethod
    async def get_content(self, mailer_id: int) -> BaseContent:
        pass

    @abstractmethod
    async def set_content(self, mailer_id: int, content: BaseContent) -> None:
        pass

    @abstractmethod
    async def get_chats(self, mailer_id: int) -> ChatEngine:
        pass

    @abstractmethod
    async def set_chats(self, mailer_id: int, chats: ChatEngine) -> None:
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
