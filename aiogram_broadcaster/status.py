from enum import Enum


class Status(str, Enum):
    STARTED = "started"
    STOPPED = "stopped"
    COMPLETED = "completed"
