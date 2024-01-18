from typing import List, NamedTuple

from pydantic import BaseModel

from .types_ import ChatsIds


class MailerSettingsData(BaseModel):
    interval: float
    total_chats: int
    message_id: int
    from_chat_id: int
    notifications: bool
    protect_content: bool


class MailerData(BaseModel):
    chat_ids: List[int]
    settings: MailerSettingsData

    @classmethod
    def build(
        cls,
        *,
        chat_ids: ChatsIds,
        interval: float,
        message_id: int,
        from_chat_id: int,
        notifications: bool,
        protect_content: bool,
    ) -> "MailerData":
        return MailerData(
            chat_ids=list(set(chat_ids)),
            settings=MailerSettingsData(
                interval=interval,
                total_chats=len(set(chat_ids)),
                message_id=message_id,
                from_chat_id=from_chat_id,
                notifications=notifications,
                protect_content=protect_content,
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
