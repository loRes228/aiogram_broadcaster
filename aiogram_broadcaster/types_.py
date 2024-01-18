from datetime import timedelta
from typing import Iterable, Type, Union


ChatsIds = Iterable[Union[int, str]]
Interval = Union[float, int, timedelta]
ExceptionType = Union[Type[Exception], bool]
