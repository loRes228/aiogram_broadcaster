import pytest

from aiogram_broadcaster.event.observer import EventObserver


class TestEventObserver:
    def test_register_callback(self):
        observer = EventObserver()

        def callback():
            pass

        observer.register(callback)
        assert len(observer) == 1
        assert list(observer)[0] == callback

    def test_register_multiple_callbacks(self):
        observer = EventObserver()

        def callback1():
            pass

        def callback2():
            pass

        observer.register(callback1, callback2)
        assert len(observer) == 2
        callbacks = list(observer)
        assert callback1 in callbacks
        assert callback2 in callbacks

    def test_register_no_callbacks(self):
        observer = EventObserver()

        with pytest.raises(
            ValueError,
            match="At least one callback must be provided to register.",
        ):
            observer.register()

    def test_callable_registration(self):
        observer = EventObserver()

        @observer()
        def callback():
            pass

        assert len(observer) == 1
        assert list(observer)[0] == callback

    def test_register_fluent(self):
        observer = EventObserver()

        def callback():
            pass

        assert observer.register(callback) == observer
