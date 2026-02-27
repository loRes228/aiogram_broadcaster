from typing import Optional, Protocol
from time import time_ns


class IntContainer(Protocol):
    def __contains__(self, item: int) -> bool: ...


def generate_id(container: Optional[IntContainer] = None) -> int:
    while True:
        new_id = time_ns()
        if not container or new_id not in container:
            return new_id
