from asyncio import create_task
from typing import TYPE_CHECKING, Any, Coroutine, Optional


if TYPE_CHECKING:
    from asyncio import Task


class TaskManager:
    task: Optional["Task[Any]"]
    waited: bool

    __slots__ = (
        "task",
        "waited",
    )

    def __init__(self) -> None:
        self.task = None
        self.waited = False

    def start(self, coroutine: Coroutine[Any, Any, Any], /) -> None:
        if self.task:
            return
        self.task = create_task(coroutine)
        self.task.add_done_callback(self._on_task_done)

    async def wait(self) -> None:
        if not self.task or self.waited:
            return
        self.waited = True
        await self.task

    def _on_task_done(self, _: "Task[Any]") -> None:
        self.task = None
        self.waited = False
