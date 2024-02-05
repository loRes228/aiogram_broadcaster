from enum import Enum


class Strategy(str, Enum):
    SEND = "send"
    COPY = "copy"
    FORWARD = "forward"
