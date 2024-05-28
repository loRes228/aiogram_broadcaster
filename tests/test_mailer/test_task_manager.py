import asyncio
import unittest.mock

import pytest

from aiogram_broadcaster.mailer.task_manager import TaskManager


@pytest.fixture()
def task_manager():
    return TaskManager()


@pytest.fixture()
def task_coroutine():
    async def task_coroutine():
        pass

    return task_coroutine()


class TestTaskManager:
    async def test_start(self, task_manager, task_coroutine):
        assert not task_manager.started
        task_manager.start(task_coroutine)
        assert task_manager.started
        assert not task_manager.waited

    async def test_start_already_started(self, task_manager, task_coroutine):
        task_manager.start(task_coroutine)
        with pytest.raises(
            RuntimeError,
            match="Task is already started.",
        ):
            task_manager.start(task_coroutine)

    async def test_wait(self, task_manager, task_coroutine):
        task_manager.start(task_coroutine)
        with unittest.mock.patch.object(
            target=task_manager,
            attribute="wait",
            new_callable=unittest.mock.AsyncMock,
        ) as mocked_wait:
            await task_manager.wait()
            mocked_wait.assert_awaited_once()

    async def test_wait_no_task(self, task_manager):
        with pytest.raises(RuntimeError, match="No task for wait."):
            await task_manager.wait()

    async def test_wait_already_waited(self, task_manager, task_coroutine):
        task_manager.start(task_coroutine)

        with pytest.raises(RuntimeError, match="Task is already waited."):
            await asyncio.gather(task_manager.wait(), task_manager.wait())

    async def test_on_task_done(self, task_manager, task_coroutine):
        task_manager.start(task_coroutine)
        assert task_manager.started
        assert not task_manager.waited

        task_manager._on_task_done(task_coroutine)
        assert not task_manager.started
        assert not task_manager.waited
