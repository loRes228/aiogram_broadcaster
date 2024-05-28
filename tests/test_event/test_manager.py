import unittest.mock

import pytest

from aiogram_broadcaster.event.manager import EventManager


class TestEventManager:
    async def test_emit_event(self):
        manager = EventManager()

        mock_callback1 = unittest.mock.Mock(return_value={"data1": "value1"})
        mock_callback2 = unittest.mock.Mock(return_value={"data2": "value2"})

        manager.started.register(mock_callback1)
        manager.started.register(mock_callback2)

        context = {"initial": "context"}
        result = await manager.emit_event("started", **context)

        assert result == {"data1": "value1", "data2": "value2"}
        mock_callback1.assert_called_once_with(**context)
        mock_callback2.assert_called_once_with(**context, data1="value1")

    async def test_emit_event_no_callbacks(self):
        manager = EventManager()

        context = {"initial": "context"}
        result = await manager.emit_event("started", **context)

        assert result == {}

    async def test_emit_event_with_non_dict_result(self):
        manager = EventManager()

        mock_callback = unittest.mock.Mock(return_value="non_dict_result")
        manager.started.register(mock_callback)

        context = {"initial": "context"}
        result = await manager.emit_event("started", **context)

        assert result == {}
        mock_callback.assert_called_once_with(**context)

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
    async def test_emit_methods(self, event_name):
        manager = EventManager()

        with unittest.mock.patch.object(
            target=manager,
            attribute="emit_event",
        ) as mocked_emit_event:
            emit_method = getattr(manager, f"emit_{event_name}")
            await emit_method(data1="value1")
            mocked_emit_event.assert_called_once_with(event_name, data1="value1")
