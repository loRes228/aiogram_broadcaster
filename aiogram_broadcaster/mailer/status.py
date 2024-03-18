from enum import Enum, auto


class MailerStatus(Enum):
    DESTROYED = auto()
    STOPPED = auto()
    STARTED = auto()
    COMPLETED = auto()
