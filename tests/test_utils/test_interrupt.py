import pytest

from aiogram_broadcaster.utils.interrupt import Interrupt, interrupt, suppress_interrupt


class TestInterrupt:
    @pytest.mark.parametrize("exception", suppress_interrupt.args)
    def test_suppress_interrupt(self, exception):
        with suppress_interrupt():
            raise exception

    def test_suppress_other_exception(self):
        with pytest.raises(KeyError), suppress_interrupt():
            raise KeyError

    def test_raise_interrupt(self):
        with pytest.raises(Interrupt):
            interrupt()
