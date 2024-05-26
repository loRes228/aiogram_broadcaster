import re
import unittest.mock
from string import Template

import pydantic
import pytest

from aiogram_broadcaster.placeholder import PlaceholderItem, PlaceholderManager, PlaceholderRouter
from aiogram_broadcaster.utils.interrupt import interrupt


@pytest.fixture()
def valid_model():
    return pydantic.create_model(
        "ValidModel",
        text=(str, "Hello, $name!"),
    )()


@pytest.fixture()
def without_text_field_model():
    return pydantic.create_model(
        "WithoutTextFieldModel",
        foo=(str, "any text"),
    )()


@pytest.fixture()
def invalid_type_text_field_model():
    return pydantic.create_model(
        "InvalidTypeTextFieldModel",
        caption=(int, 1111),
    )()


class MyPlaceholderItem(PlaceholderItem, key="test_key"):
    async def __call__(self):
        return "test_value"


@pytest.fixture()
def placeholder_item():
    return MyPlaceholderItem()


class TestPlaceholderItem:
    def test_class_attrs(self):
        assert MyPlaceholderItem.key == "test_key"

    def test_repr(self, placeholder_item):
        assert repr(placeholder_item) == "MyPlaceholderItem(key='test_key')"

    def test_subclass_without_key(self):
        with pytest.raises(
            ValueError,
            match="Missing required argument 'key' when subclassing PlaceholderItem.",
        ):

            class InvalidPlaceholderItem(PlaceholderItem):
                async def __call__(self):
                    return


class TestPlaceholderRouter:
    def test_add(self):
        router = PlaceholderRouter()
        router.add(key="test_key", value="test_value")
        router["test_key_2"] = "test_value_2"

        assert "test_key" in router
        assert "test_key_2" in router
        assert router["test_key"] == "test_value"
        assert router["test_key_2"] == "test_value_2"
        assert dict(router) == {"test_key": "test_value", "test_key_2": "test_value_2"}

        assert "test_key" in router.items
        assert "test_key_2" in router.items
        assert router.items["test_key"] == "test_value"
        assert router.items["test_key_2"] == "test_value_2"
        assert router.items == {"test_key": "test_value", "test_key_2": "test_value_2"}

        assert tuple(router.chain_keys) == ("test_key", "test_key_2")
        assert tuple(router.chain_items) == (
            ("test_key", "test_value"),
            ("test_key_2", "test_value_2"),
        )

    def test_call(self):
        router = PlaceholderRouter()

        @router(key="test_key")
        async def decorated_callback():
            return

        assert router["test_key"].callback == decorated_callback

    def test_add_already_exists_key(self):
        router = PlaceholderRouter()
        router["test_key"] = "test_value"

        with pytest.raises(
            ValueError,
            match="Key 'test_key' is already exists.",
        ):
            router.add(key="test_key", value="test_value")

    def test_fluent_add(self):
        router = PlaceholderRouter()
        assert router.add(key="test", value="test") == router

    def test_register(self, placeholder_item):
        router = PlaceholderRouter()
        router.register(placeholder_item)
        assert "test_key" in router
        assert router["test_key"].callback == placeholder_item.__call__
        assert router.items["test_key"].callback == placeholder_item.__call__

    def test_register_without_args(self):
        router = PlaceholderRouter()
        with pytest.raises(
            ValueError,
            match="At least one placeholder item must be provided to register.",
        ):
            router.register()

    def test_register_invalid_type(self):
        router = PlaceholderRouter()
        with pytest.raises(
            TypeError,
            match="The placeholder item must be an instance of PlaceholderItem, not a str.",
        ):
            router.register("invalid type")

    def test_register_fluent(self, placeholder_item):
        router = PlaceholderRouter()
        assert router.register(placeholder_item) == router

    def test_attach(self):
        router = PlaceholderRouter()
        router.attach({"test_key": "test_value"}, test_key_2="test_value_2")
        assert router.items == {"test_key": "test_value", "test_key_2": "test_value_2"}

    def test_attach_without_args(self):
        router = PlaceholderRouter()
        with pytest.raises(
            ValueError,
            match="At least one keyword argument must be specified to attaching.",
        ):
            router.attach()

    def test_fluent_attach(self):
        router = PlaceholderRouter()
        assert router.attach(key="value") == router

    def test_include(self):
        router1 = PlaceholderRouter()
        router2 = PlaceholderRouter()
        router1["test_key"] = "test_value"
        router2["test_key_2"] = "test_value_2"
        router1.include(router2)
        assert router1.items == {"test_key": "test_value"}
        assert router2.items == {"test_key_2": "test_value_2"}
        assert dict(router1) == {"test_key": "test_value", "test_key_2": "test_value_2"}

    def test_include_collusion(self):
        router1 = PlaceholderRouter(name="placeholder1")
        router2 = PlaceholderRouter(name="placeholder2")
        router1["test_key"] = "test_value"
        router2["test_key"] = "test_value_2"
        with pytest.raises(
            ValueError,
            match=re.escape(
                "The PlaceholderRouter(name='placeholder1') already has the keys: ['test_key'].",
            ),
        ):
            router1.include(router2)


class TestPlaceholderManager:
    async def test_fetch_data(self, placeholder_item):
        manager = PlaceholderManager()
        manager.register(placeholder_item)
        manager["test_key_2"] = "test_value_2"
        assert await manager.fetch_data({"test_key", "test_key_2"}) == {
            "test_key": "test_value",
            "test_key_2": "test_value_2",
        }
        assert await manager.fetch_data({}) == {}
        assert await manager.fetch_data({"not_exists_key"}) == {}

    async def test_fetch_data_calls_callback(self, placeholder_item):
        manager = PlaceholderManager()

        @manager(key="test_key")
        async def callback(**kwargs):
            return "test_value"

        with unittest.mock.patch.object(
            target=manager["test_key"],
            attribute="call",
            new_callable=unittest.mock.AsyncMock,
        ) as mocked_callback:
            await manager.fetch_data({"test_key"}, test_param=1)
            mocked_callback.assert_called_once_with(test_param=1)

    def test_extract_text_field(
        self,
        valid_model,
        without_text_field_model,
        invalid_type_text_field_model,
    ):
        manager = PlaceholderManager()
        assert manager.extract_text_field(model=valid_model) == ("text", "Hello, $name!")
        assert manager.extract_text_field(model=without_text_field_model) is None
        assert manager.extract_text_field(model=invalid_type_text_field_model) is None

    def test_extract_keys(self):
        manager = PlaceholderManager()
        assert manager.extract_keys(template=Template("Hello, $name!")) == {"name"}
        assert manager.extract_keys(template=Template("$mention $age")) == {"mention", "age"}
        assert manager.extract_keys(template=Template("text without vars")) == set()

    async def test_render_with_placeholders(self, valid_model):
        manager = PlaceholderManager()
        manager["name"] = "John"
        rendered_model = await manager.render(valid_model)
        assert rendered_model.text == "Hello, John!"

    async def test_render_without_placeholders(self, valid_model):
        manager = PlaceholderManager()
        rendered_model = await manager.render(valid_model)
        assert rendered_model.text == "Hello, $name!"

    async def test_render_with_excluded_keys(self, valid_model):
        manager = PlaceholderManager()
        manager["name"] = "John"
        rendered_model = await manager.render(valid_model, {"name"})
        assert rendered_model.text == "Hello, $name!"

    async def test_render_with_no_keys(self, valid_model):
        manager = PlaceholderManager()
        manager["unused_key"] = "Some value"
        rendered_model = await manager.render(valid_model)
        assert rendered_model.text == "Hello, $name!"

    async def test_render_with_empty_exclude_keys(self, valid_model):
        manager = PlaceholderManager()
        manager["name"] = "John"
        rendered_model = await manager.render(valid_model)
        assert rendered_model.text == "Hello, John!"

    async def test_render_with_non_matching_keys(self, valid_model):
        manager = PlaceholderManager()
        manager["non_matching_key"] = "Some value"
        rendered_model = await manager.render(valid_model)
        assert rendered_model.text == "Hello, $name!"

    async def test_render_without_text_field(self, without_text_field_model):
        manager = PlaceholderManager()
        manager["name"] = "John"
        rendered_model = await manager.render(without_text_field_model)
        assert rendered_model == without_text_field_model

    async def test_render_with_invalid_type_text_field(self, invalid_type_text_field_model):
        manager = PlaceholderManager()
        manager["name"] = "John"
        rendered_model = await manager.render(invalid_type_text_field_model)
        assert rendered_model == invalid_type_text_field_model

    async def test_render_without_data(self, valid_model):
        manager = PlaceholderManager()
        manager["name"] = interrupt
        rendered_model = await manager.render(valid_model)
        assert rendered_model == valid_model
