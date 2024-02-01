from typing import NamedTuple


class Statistic(NamedTuple):
    total_chats: int
    success: int
    failed: int

    @property
    def ratio(self) -> float:
        return (self.success / self.total_chats) * 100
