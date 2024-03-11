from typing import Container
from uuid import uuid4


class AttemptsExceededError(Exception):
    pass


def generate_id(
    container: Container[int] = set(),
    attempts: int = 1_000,
) -> int:
    for _ in range(attempts):
        new_id = hash(uuid4())
        if new_id not in container:
            return new_id
    raise AttemptsExceededError("Maximum attempts exceeded while generating ID.")
