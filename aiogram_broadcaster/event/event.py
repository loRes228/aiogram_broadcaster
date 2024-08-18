from typing import Optional

from aiogram_broadcaster.utils.chain import Chain

from .observer import EventObserver


class Event(Chain["Event"], sub_name="event"):
    def __init__(self, name: Optional[str] = None) -> None:
        super().__init__(name=name)

        self.created = EventObserver()
        self.deleted = EventObserver()
        self.started = EventObserver()
        self.stopped = EventObserver()
        self.completed = EventObserver()
        self.failed_send = EventObserver()
        self.success_send = EventObserver()
        self.observers: dict[str, EventObserver] = {
            "created": self.created,
            "deleted": self.deleted,
            "started": self.started,
            "stopped": self.stopped,
            "completed": self.completed,
            "failed_send": self.failed_send,
            "success_send": self.success_send,
        }
