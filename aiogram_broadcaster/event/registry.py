from typing import Dict, Optional

from aiogram_broadcaster.utils.chain import Chain

from .observer import EventObserver


class EventRegistry(Chain["EventRegistry"], sub_name="event"):
    started: EventObserver
    stopped: EventObserver
    completed: EventObserver
    before_sent: EventObserver
    success_sent: EventObserver
    failed_sent: EventObserver
    observers: Dict[str, EventObserver]

    def __init__(self, name: Optional[str] = None) -> None:
        super().__init__(name=name)

        self.started = EventObserver()
        self.stopped = EventObserver()
        self.completed = EventObserver()
        self.before_sent = EventObserver()
        self.success_sent = EventObserver()
        self.failed_sent = EventObserver()
        self.observers = {
            "started": self.started,
            "stopped": self.stopped,
            "completed": self.completed,
            "before_sent": self.before_sent,
            "success_sent": self.success_sent,
            "failed_sent": self.failed_sent,
        }

    def __getitem__(self, item: str) -> EventObserver:
        return self.observers[item]
