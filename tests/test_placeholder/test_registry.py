import re

import pytest

from aiogram_broadcaster.placeholder.item import PlaceholderItem
from aiogram_broadcaster.placeholder.placeholder import Placeholder
from aiogram_broadcaster.placeholder.registry import PlaceholderRegistry


class DummyPlaceholderItem(PlaceholderItem, key="test_key"):
    async def __call__(self, **kwargs):
        return "test_value"


class TestPlaceholderRegistry:
    def test_initialization(self):
        registry = PlaceholderRegistry(name="test_registry")
        assert registry.name == "test_registry"
        assert registry.placeholders == set()

    def test_add_placeholder(self):
        registry = PlaceholderRegistry()
        registry["key1"] = "value1"
        assert registry.placeholders == {Placeholder(key="key1", value="value1")}

    def test_register_placeholder_items(self):
        registry = PlaceholderRegistry()
        item1 = DummyPlaceholderItem()
        item2 = DummyPlaceholderItem()
        registry.register(item1, item2)
        assert registry.placeholders == {item1.as_placeholder(), item2.as_placeholder()}
        registry = PlaceholderRegistry()
        assert registry.register(item2) == registry
        with pytest.raises(
            ValueError,
            match="At least one placeholder item must be provided to register.",
        ):
            registry.register()

    def test_add_method(self):
        registry = PlaceholderRegistry()
        registry.add(key1="value1", key2="value2")
        assert registry.placeholders == {
            Placeholder(key="key1", value="value1"),
            Placeholder(key="key2", value="value2"),
        }
        assert registry.add({"key1": "value1"}) == registry
        with pytest.raises(ValueError, match="At least one argument must be provided."):
            registry.add()

    def test_items_property(self):
        registry = PlaceholderRegistry()
        registry["key1"] = "value1"
        registry["key2"] = "value2"
        assert sorted(registry.items) == [("key1", "value1"), ("key2", "value2")]

    def test_keys_property(self):
        registry = PlaceholderRegistry()
        registry["key1"] = "value1"
        registry["key2"] = "value2"
        assert registry.keys == {"key1", "key2"}

    def test_chain_placeholders_property(self):
        registry1 = PlaceholderRegistry()
        registry2 = PlaceholderRegistry()
        registry1["key1"] = "value1"
        registry2["key2"] = "value2"
        registry1.bind(registry2)
        assert set(registry1.chain_placeholders) == {
            Placeholder(key="key1", value="value1"),
            Placeholder(key="key2", value="value2"),
        }

    def test_chain_items_property(self):
        registry1 = PlaceholderRegistry()
        registry2 = PlaceholderRegistry()
        registry1["key1"] = "value1"
        registry2["key2"] = "value2"
        registry1.bind(registry2)
        assert set(registry1.chain_items) == {("key1", "value1"), ("key2", "value2")}

    def test_chain_keys_property(self):
        registry1 = PlaceholderRegistry()
        registry2 = PlaceholderRegistry()
        registry1["key1"] = "value1"
        registry2["key2"] = "value2"
        registry1.bind(registry2)
        assert set(registry1.chain_keys) == {"key1", "key2"}

    def test_iter(self):
        registry = PlaceholderRegistry()
        registry["key1"] = "value1"
        registry["key2"] = "value2"
        assert sorted(registry) == [("key1", "value1"), ("key2", "value2")]

    def test_contains(self):
        registry = PlaceholderRegistry()
        registry["key1"] = "value1"
        assert "key1" in registry
        assert "key2" not in registry

    def test_chain_bind_no_collision(self):
        registry1 = PlaceholderRegistry(name="registry1")
        registry2 = PlaceholderRegistry(name="registry2")
        registry1["key1"] = "value1"
        registry2["key2"] = "value2"

        registry1.bind(registry2)
        assert set(registry1.chain_placeholders) == {
            Placeholder(key="key1", value="value1"),
            Placeholder(key="key2", value="value2"),
        }

    def test_chain_bind_with_collision(self):
        registry1 = PlaceholderRegistry(name="registry1")
        registry2 = PlaceholderRegistry(name="registry2")
        registry1["key1"] = "value1"
        registry2["key1"] = "value2"

        with pytest.raises(
            RuntimeError,
            match=re.escape(
                "Collision keys=['key1'] between PlaceholderRegistry(name='registry1') "
                "and PlaceholderRegistry(name='registry2').",
            ),
        ):
            registry1.bind(registry2)

    def test_call(self):
        registry = PlaceholderRegistry()

        @registry(key="test_key")
        async def callback():
            return

        assert registry.placeholders == {Placeholder(key="test_key", value=callback)}
        assert registry["test_key"] == callback
