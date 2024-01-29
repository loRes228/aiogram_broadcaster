from abc import ABC, abstractmethod
from typing import List

from aiogram_broadcaster.data import MailerData


class BaseStorage(ABC):
    @abstractmethod
    async def get_mailer_ids(self) -> List[int]:
        pass

    @abstractmethod
    async def get_data(self, mailer_id: int) -> MailerData:
        pass

    @abstractmethod
    async def set_data(self, mailer_id: int, data: MailerData) -> None:
        pass

    @abstractmethod
    async def delete_data(self, mailer_id: int) -> None:
        pass

    @abstractmethod
    async def pop_chat(self, mailer_id: int) -> None:
        pass


class NullStorage(BaseStorage):
    async def get_mailer_ids(self) -> List[int]:  # type: ignore[empty-body]
        pass

    async def get_data(self, mailer_id: int) -> MailerData:  # type: ignore[empty-body]
        pass

    async def set_data(self, mailer_id: int, data: MailerData) -> None:
        pass

    async def delete_data(self, mailer_id: int) -> None:
        pass

    async def pop_chat(self, mailer_id: int) -> None:
        pass
