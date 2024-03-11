from pydantic import BaseModel, Field


class MailerSettings(BaseModel):
    interval: float = Field(default=1, ge=0)
    disable_events: bool = False
    preserved: bool = Field(default=True, exclude=True)
