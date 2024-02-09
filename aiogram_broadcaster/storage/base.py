from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Tuple


if TYPE_CHECKING:
    from aiogram_broadcaster.chat_manager import ChatState
    from aiogram_broadcaster.settings import (
        ChatsSettings,
        MailerSettings,
        MessageSettings,
        Settings,
    )


class BaseMailerStorage(ABC):
    @abstractmethod
    async def get_mailer_ids(self) -> Tuple[int, ...]:
        pass

    @abstractmethod
    async def delete(self, mailer_id: int) -> None:
        pass

    @abstractmethod
    async def get(self, mailer_id: int) -> "Settings":
        pass

    @abstractmethod
    async def set(self, mailer_id: int, settings: "Settings") -> None:
        pass

    @abstractmethod
    async def get_chats(self, mailer_id: int) -> "ChatsSettings":
        pass

    @abstractmethod
    async def get_mailer(self, mailer_id: int) -> "MailerSettings":
        pass

    @abstractmethod
    async def get_message(self, mailer_id: int) -> "MessageSettings":
        pass

    @abstractmethod
    async def set_chats(self, mailer_id: int, settings: "ChatsSettings") -> None:
        pass

    @abstractmethod
    async def set_mailer(self, mailer_id: int, settings: "MailerSettings") -> None:
        pass

    @abstractmethod
    async def set_message(self, mailer_id: int, settings: "MessageSettings") -> None:
        pass

    @abstractmethod
    async def set_chat_state(self, mailer_id: int, chat: int, state: "ChatState") -> None:
        pass


class NullMailerStorage(BaseMailerStorage):
    async def get_mailer_ids(self) -> Tuple[int, ...]:
        return ()

    async def delete(self, mailer_id: int) -> None:
        pass

    async def get(self, mailer_id: int) -> "Settings":  # type: ignore[empty-body]
        pass

    async def set(self, mailer_id: int, settings: "Settings") -> None:
        pass

    async def get_chats(self, mailer_id: int) -> "ChatsSettings":  # type: ignore[empty-body]
        pass

    async def get_mailer(self, mailer_id: int) -> "MailerSettings":  # type: ignore[empty-body]
        pass

    async def get_message(self, mailer_id: int) -> "MessageSettings":  # type: ignore[empty-body]
        pass

    async def set_chats(self, mailer_id: int, settings: "ChatsSettings") -> None:
        pass

    async def set_mailer(self, mailer_id: int, settings: "MailerSettings") -> None:
        pass

    async def set_message(self, mailer_id: int, settings: "MessageSettings") -> None:
        pass

    async def set_chat_state(self, mailer_id: int, chat: int, state: "ChatState") -> None:
        pass
