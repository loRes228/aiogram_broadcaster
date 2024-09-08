from enum import Enum, auto


class MailerStatus(Enum):
    STOPPED = auto()
    STARTED = auto()
    COMPLETED = auto()
