from datetime import timedelta
from typing import Iterable, Sequence, Union


ChatsIds = Union[Iterable[Union[int, str]], Sequence[Union[int, str]]]
Interval = Union[float, int, timedelta]
