from aiogram_broadcaster.placeholder.item import PlaceholderItem
from aiogram_broadcaster.placeholder.placeholder import Placeholder


class DummyPlaceholderItem(PlaceholderItem, key="test_key"):
    async def __call__(self, **kwargs):
        return "test_value"


class TestPlaceholderItem:
    def test_key_assignment(self):
        assert DummyPlaceholderItem.key == "test_key"

    def test_repr(self):
        item = DummyPlaceholderItem()
        assert repr(item) == "DummyPlaceholderItem(key='test_key')"

    def test_as_placeholder(self):
        item = DummyPlaceholderItem()
        placeholder = item.as_placeholder()
        assert isinstance(placeholder, Placeholder)
        assert placeholder.key == "test_key"
        assert placeholder.value == item.__call__
