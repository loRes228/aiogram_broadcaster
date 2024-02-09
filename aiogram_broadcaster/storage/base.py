from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List


if TYPE_CHECKING:
    from aiogram_broadcaster.chat_manager import ChatState
    from aiogram_broadcaster.settings import Settings


class BaseMailerStorage(ABC):
    @abstractmethod
    async def get_mailer_ids(self) -> List[int]:
        pass

    @abstractmethod
    async def delete_settings(self, mailer_id: int) -> None:
        pass

    @abstractmethod
    async def get_settings(self, mailer_id: int) -> "Settings":
        pass

    @abstractmethod
    async def set_settings(
        self,
        mailer_id: int,
        settings: "Settings",
    ) -> None:
        pass

    @abstractmethod
    async def set_chat_state(
        self,
        mailer_id: int,
        chat: int,
        state: "ChatState",
    ) -> None:
        pass


class NullMailerStorage(BaseMailerStorage):
    async def get_mailer_ids(self) -> List[int]:
        return []

    async def delete_settings(self, mailer_id: int) -> None:
        pass

    async def get_settings(self, mailer_id: int) -> "Settings":  # type: ignore[empty-body]
        pass

    async def set_settings(
        self,
        mailer_id: int,
        settings: "Settings",
    ) -> None:
        pass

    async def set_chat_state(
        self,
        mailer_id: int,
        chat: int,
        state: "ChatState",
    ) -> None:
        pass
