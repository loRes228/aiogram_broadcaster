from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field, SerializeAsAny

from aiogram_broadcaster.contents import BaseContent
from aiogram_broadcaster.mailer.chat_engine import ChatEngine
from aiogram_broadcaster.mailer.settings import MailerSettings


class StorageRecord(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    content: SerializeAsAny[BaseContent]
    chats: ChatEngine
    settings: MailerSettings
    bot: int
    data: Dict[str, Any] = Field(default_factory=dict)
