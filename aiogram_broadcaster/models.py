from typing import List, NamedTuple

from aiogram.types import Message
from pydantic import BaseModel

from .types_ import ChatsIds


class MailerSettingsData(BaseModel):
    message: Message
    interval: float
    total_chats: int
    disable_notification: bool


class MailerData(BaseModel):
    chat_ids: List[int]
    settings: MailerSettingsData

    @classmethod
    def build(
        cls,
        *,
        chat_ids: ChatsIds,
        message: Message,
        interval: float,
        disable_notification: bool,
    ) -> "MailerData":
        chat_ids = set(chat_ids)
        return MailerData(
            chat_ids=list(chat_ids),
            settings=MailerSettingsData(
                message=message,
                interval=interval,
                total_chats=len(chat_ids),
                disable_notification=disable_notification,
            ),
        )

    @classmethod
    def build_from_json(
        cls,
        chat_ids: List[int],
        settings: str,
    ) -> "MailerData":
        return MailerData(
            chat_ids=chat_ids,
            settings=MailerSettingsData.model_validate_json(settings),
        )


class BroadcastStatistic(NamedTuple):
    total_chats: int
    success: int
    failed: int
    ratio: float
