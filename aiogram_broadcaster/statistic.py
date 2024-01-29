from dataclasses import dataclass, field


@dataclass
class Statistic:
    total_chats: int
    success: int
    failed: int
    ratio: float = field(init=False)

    def __post_init__(self) -> None:
        self.ratio = (self.success / self.total_chats) * 100
