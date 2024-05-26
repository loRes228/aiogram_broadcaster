import unittest.mock

import pytest

from aiogram_broadcaster.event import EventManager, EventObserver, EventRouter


async def callback():
    return {"test_key": "test_value"}


async def second_callback():
    return {"test_key_2": "test_value_2"}


class TestEventObserver:
    def test_init(self):
        observer = EventObserver()
        assert observer.callbacks == []

    def test_register(self):
        observer = EventObserver()
        observer.register(callback)
        assert tuple(observer) == (callback,)
        assert len(observer) == 1

    def test_register_many_callbacks(self):
        observer = EventObserver()
        observer.register(callback, second_callback)
        assert tuple(observer) == (callback, second_callback)
        assert len(observer) == 2

    def test_call(self):
        observer = EventObserver()

        @observer()
        async def decorated_callback():
            return

        assert tuple(observer) == (decorated_callback,)
        assert len(observer) == 1

    def test_register_without_args(self):
        observer = EventObserver()
        with pytest.raises(
            ValueError,
            match="At least one callback must be provided to register.",
        ):
            observer.register()

    def test_register_no_callable(self):
        observer = EventObserver()
        with pytest.raises(
            TypeError,
            match="The callback must be callable.",
        ):
            observer.register("invalid type")

    def test_fluent_register(self):
        observer = EventObserver()
        assert observer.register(callback) == observer


class TestEventRouter:
    def test_observers(self):
        router = EventRouter()
        assert router.started == router.observers["started"] == router["started"]
        assert router.stopped == router.observers["stopped"] == router["stopped"]
        assert router.completed == router.observers["completed"] == router["completed"]
        assert router.before_sent == router.observers["before_sent"] == router["before_sent"]
        assert router.success_sent == router.observers["success_sent"] == router["success_sent"]
        assert router.failed_sent == router.observers["failed_sent"] == router["failed_sent"]


@pytest.mark.parametrize(
    "event_name",
    [
        "started",
        "stopped",
        "completed",
        "before_sent",
        "success_sent",
        "failed_sent",
    ],
)
class TestEventManager:
    async def test_emit_event(self, event_name):
        manager = EventManager()
        manager.observers[event_name].register(callback, second_callback)
        result = await manager.emit_event(event_name)
        assert result == {"test_key": "test_value", "test_key_2": "test_value_2"}

    async def test_emit_methods(self, event_name):
        manager = EventManager()
        with unittest.mock.patch.object(
            target=manager,
            attribute="emit_event",
            new_callable=unittest.mock.AsyncMock,
        ) as mocked_emit_event:
            emit_method = getattr(manager, f"emit_{event_name}")
            await emit_method(test_param=1)
            mocked_emit_event.assert_called_once_with(event_name, test_param=1)
