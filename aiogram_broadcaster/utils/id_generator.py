from typing import Optional, Protocol
from uuid import uuid4


class IntContainer(Protocol):
    def __contains__(self, item: int) -> bool: ...


def generate_id(container: Optional[IntContainer] = None) -> int:
    while True:
        new_id = hash(uuid4())
        if not container or new_id not in container:
            return new_id
