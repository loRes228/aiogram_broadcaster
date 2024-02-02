from abc import ABC, abstractmethod
from typing import List

from aiogram_broadcaster.data import Data


class BaseMailerStorage(ABC):
    @abstractmethod
    async def get_mailer_ids(self) -> List[int]:
        pass

    @abstractmethod
    async def set_data(self, mailer_id: int, data: Data) -> None:
        pass

    @abstractmethod
    async def get_data(self, mailer_id: int) -> Data:
        pass

    @abstractmethod
    async def delete_data(self, mailer_id: int) -> None:
        pass

    @abstractmethod
    async def pop_chat(self, mailer_id: int) -> None:
        pass


class NullMailerStorage(BaseMailerStorage):
    async def get_mailer_ids(self) -> List[int]:
        return []

    async def set_data(self, mailer_id: int, data: Data) -> None:
        pass

    async def get_data(self, mailer_id: int) -> Data:  # type: ignore[empty-body]
        pass

    async def delete_data(self, mailer_id: int) -> None:
        pass

    async def pop_chat(self, mailer_id: int) -> None:
        pass
