from dataclasses import dataclass
from sys import version_info
from typing import Any, Dict, Optional


_dataclass_properties: Dict[str, Any] = {}
if version_info >= (3, 10):
    _dataclass_properties.update(slots=True, kw_only=True)


@dataclass(**_dataclass_properties)
class DefaultMailerProperties:
    interval: float = 0
    dynamic_interval: bool = False
    run_on_startup: bool = False
    handle_retry_after: bool = False
    destroy_on_complete: bool = False
    preserve: bool = False

    def __post_init__(self) -> None:
        if self.interval < 0:
            raise ValueError("The interval must be greater than or equal to 0.")

    def prepare(
        self,
        *,
        interval: Optional[float] = None,
        dynamic_interval: Optional[bool] = None,
        run_on_startup: Optional[bool] = None,
        handle_retry_after: Optional[bool] = None,
        destroy_on_complete: Optional[bool] = None,
        preserve: Optional[bool] = None,
    ) -> "DefaultMailerProperties":
        if interval is None:
            interval = self.interval
        if dynamic_interval is None:
            dynamic_interval = self.dynamic_interval
        if run_on_startup is None:
            run_on_startup = self.run_on_startup
        if handle_retry_after is None:
            handle_retry_after = self.handle_retry_after
        if destroy_on_complete is None:
            destroy_on_complete = self.destroy_on_complete
        if preserve is None:
            preserve = self.preserve
        return DefaultMailerProperties(
            interval=interval,
            dynamic_interval=dynamic_interval,
            run_on_startup=run_on_startup,
            handle_retry_after=handle_retry_after,
            destroy_on_complete=destroy_on_complete,
            preserve=preserve,
        )
