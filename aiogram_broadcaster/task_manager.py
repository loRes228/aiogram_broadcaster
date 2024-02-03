from asyncio import create_task
from typing import TYPE_CHECKING, Any, Optional

from aiogram.dispatcher.event.handler import CallbackType


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

    def start(self, callback: CallbackType) -> None:
        if self.task:
            return
        self.task = create_task(callback())
        self.task.add_done_callback(self._on_task_done)

    async def wait(self) -> None:
        if not self.task or self.waited:
            return
        self.waited = True
        await self.task

    def _on_task_done(self, _: "Task[Any]") -> None:
        self.task = None
        self.waited = False
