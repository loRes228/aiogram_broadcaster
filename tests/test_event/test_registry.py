from aiogram_broadcaster.event.registry import EventRegistry


class TestEventRegistry:
    def test_observers(self):
        registry = EventRegistry()
        assert registry.started == registry.observers["started"] == registry["started"]
        assert registry.stopped == registry.observers["stopped"] == registry["stopped"]
        assert registry.completed == registry.observers["completed"] == registry["completed"]
        assert registry.before_sent == registry.observers["before_sent"] == registry["before_sent"]
        assert (
            registry.success_sent == registry.observers["success_sent"] == registry["success_sent"]
        )
        assert registry.failed_sent == registry.observers["failed_sent"] == registry["failed_sent"]
