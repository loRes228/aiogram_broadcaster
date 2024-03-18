from typing import Literal, Optional, Set, Union

from pydantic import BaseModel, Field


class MailerSettings(BaseModel):
    interval: float = Field(default=1, ge=0)
    run_on_startup: bool = False
    disable_events: bool = False
    handle_retry_after: bool = False
    destroy_on_complete: bool = False
    exclude_placeholders: Optional[Union[Literal[True], Set[str]]] = None
