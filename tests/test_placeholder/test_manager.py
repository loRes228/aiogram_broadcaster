import unittest.mock
from string import Template

import pydantic

from aiogram_broadcaster.placeholder.manager import PlaceholderManager
from aiogram_broadcaster.utils.interrupt import Interrupt


class TestPlaceholderManager:
    async def test_fetch_data_no_select_keys(self):
        manager = PlaceholderManager()
        data = await manager.fetch_data(set())
        assert data == {}

    async def test_fetch_data_with_select_keys(self):
        manager = PlaceholderManager()
        manager["key1"] = unittest.mock.Mock(return_value="value1")
        manager["key2"] = unittest.mock.Mock(return_value="value2")
        data = await manager.fetch_data({"key1", "key2"})
        assert data == {"key1": "value1", "key2": "value2"}

    async def test_fetch_data_missing_keys(self):
        manager = PlaceholderManager()
        manager["key1"] = unittest.mock.Mock(return_value="value1")
        data = await manager.fetch_data({"key2"})
        assert data == {}

    async def test_fetch_data_interrupt(self):
        manager = PlaceholderManager()
        manager["key1"] = unittest.mock.Mock(side_effect=Interrupt)
        data = await manager.fetch_data({"key1"})
        assert data == {}

    def test_extract_text_field_found(self):
        manager = PlaceholderManager()
        model = pydantic.create_model("TestModel", caption=(str, "Hello, $name!"))
        field = manager.extract_text_field(model())
        assert field == ("caption", "Hello, $name!")

    def test_extract_text_field_not_found(self):
        manager = PlaceholderManager()
        model = pydantic.create_model("TestModel", description=(str, "Some description"))
        field = manager.extract_text_field(model())
        assert field is None

    def test_extract_keys_with_placeholders(self):
        manager = PlaceholderManager()
        template = manager.extract_keys(Template("Hello, $name!"))
        assert template == {"name"}

    def test_extract_keys_no_placeholders(self):
        manager = PlaceholderManager()
        template = manager.extract_keys(Template("Hello, world!"))
        assert template == set()

    async def test_render_no_keys(self):
        manager = PlaceholderManager()
        model = pydantic.create_model("TestModel", caption=(str, "Hello, $name!"))
        rendered_model = await manager.render(model())
        assert rendered_model == model()

    async def test_render_all_keys_excluded(self):
        manager = PlaceholderManager()
        model = pydantic.create_model("TestModel", caption=(str, "Hello, $name!"))
        rendered_model = await manager.render(model(), {"name"})
        assert rendered_model == model()

    async def test_render_no_placeholders_found(self):
        manager = PlaceholderManager()
        model = pydantic.create_model("TestModel", description=(str, "Some description"))
        rendered_model = await manager.render(model())
        assert rendered_model == model()

    async def test_render_placeholders_and_data_fetched(self):
        manager = PlaceholderManager()
        manager["name"] = unittest.mock.Mock(return_value="John")
        model = pydantic.create_model("TestModel", caption=(str, "Hello, $name!"))
        rendered_model = await manager.render(model())
        assert rendered_model == model(caption="Hello, John!")

    async def test_render_placeholders_but_no_data_fetched(self):
        manager = PlaceholderManager()
        model = pydantic.create_model("TestModel", caption=(str, "Hello, $name!"))
        rendered_model = await manager.render(model())
        assert rendered_model == model()

    async def test_render_interrupt(self):
        manager = PlaceholderManager()
        manager["name"] = unittest.mock.Mock(side_effect=Interrupt)
        model = pydantic.create_model("TestModel", caption=(str, "Hello, $name!"))
        rendered_model = await manager.render(model())
        assert rendered_model == model()

    async def test_render_empty_keys(self):
        manager = PlaceholderManager()
        manager["name"] = "test_value"
        model = pydantic.create_model("TestModel", caption=(str, "Hello, $name!"))
        rendered_model = await manager.render(model(), {"name"})
        assert rendered_model == model()

    async def test_render_without_field(self):
        manager = PlaceholderManager()
        manager["name"] = "test_value"
        model = pydantic.create_model("TestModel", not_text_field=(str, "value"))
        rendered_model = await manager.render(model())
        assert rendered_model == model()

    async def test_render_without_select_keys(self):
        manager = PlaceholderManager()
        manager["name"] = "test_value"
        manager["age"] = "test_value"
        model = pydantic.create_model("TestModel", text=(str, "Hello, $name!"))
        rendered_model = await manager.render(model(), {"name"})
        assert rendered_model == model()
