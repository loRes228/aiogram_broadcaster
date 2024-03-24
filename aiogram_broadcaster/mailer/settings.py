from typing import Literal, Optional, Set, Union

from pydantic import BaseModel, ConfigDict, Field, PositiveFloat


class MailerSettings(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    interval: PositiveFloat = 1
    run_on_startup: bool = False
    disable_events: bool = False
    handle_retry_after: bool = False
    destroy_on_complete: bool = False
    exclude_placeholders: Optional[Union[Literal[True], Set[str]]] = None
    preserved: bool = Field(default=True, exclude=True)
