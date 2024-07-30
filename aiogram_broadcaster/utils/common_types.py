from typing import Any, Callable


CallbackType = Callable[..., Any]
WrapperType = Callable[[CallbackType], CallbackType]
