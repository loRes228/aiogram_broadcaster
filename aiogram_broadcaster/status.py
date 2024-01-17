from enum import Enum


class MailerStatus(str, Enum):
    STOPPED = "stopped"
    STARTED = "started"
    COMPLETED = "completed"
