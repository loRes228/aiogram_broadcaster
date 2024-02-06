from enum import Enum, auto


class Strategy(Enum):
    SEND = auto()
    COPY = auto()
    FORWARD = auto()
