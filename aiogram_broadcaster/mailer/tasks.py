from asyncio import create_task
from typing import TYPE_CHECKING, Any, Coroutine, Optional


if TYPE_CHECKING:
    from asyncio import Task


class TaskManager:
    _task: Optional["Task[Any]"]
    _waited: bool

    def __init__(self) -> None:
        self._task = None
        self._waited = False

    @property
    def started(self) -> bool:
        return self._task is not None

    @property
    def waited(self) -> bool:
        return self._waited

    def start(self, target: Coroutine[Any, Any, Any]) -> None:
        if self._task:
            return
        self._task = create_task(target)
        self._task.add_done_callback(self._on_task_done)

    async def wait(self) -> None:
        if not self._task or self._waited:
            return
        self._waited = True
        await self._task

    def _on_task_done(self, _: "Task[Any]") -> None:
        self._task = None
        self._waited = False
