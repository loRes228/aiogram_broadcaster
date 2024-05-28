import pytest

from aiogram_broadcaster.contents.base import BaseContent
from aiogram_broadcaster.contents.key_based import KeyBasedContent


class DummyContent(BaseContent, register=False):
    async def __call__(self, **kwargs):
        return {
            "method": "dummy_method",
            **kwargs,
            **(self.model_extra or {}),
        }


class DummyKeyBasedContent(KeyBasedContent, register=False):
    async def __call__(self, **kwargs):
        return "key1"


class TestKeyBasedContent:
    async def test_key_based_content_as_method(self):
        content = DummyKeyBasedContent(
            key1=DummyContent(param="value1"),
            key2=DummyContent(param="value2"),
            default=DummyContent(param="default_value"),
        )
        result = await content.as_method(context_param="context_value")
        assert isinstance(result, dict)
        assert result == {
            "method": "dummy_method",
            "param": "value1",
            "context_param": "context_value",
        }

    async def test_key_based_content_getitem(self):
        content = DummyKeyBasedContent(
            key1=DummyContent(param="value1"),
            key2=DummyContent(param="value2"),
            default=DummyContent(param="default_value"),
        )
        assert content["key1"].param == "value1"
        assert content["key2"].param == "value2"
        assert content["key3"].param == "default_value"

    async def test_get_not_exists_key(self):
        content = DummyKeyBasedContent(
            key1=DummyContent(param="value1"),
            key2=DummyContent(param="value2"),
        )
        assert content["key1"].param == "value1"
        assert content["key2"].param == "value2"

        with pytest.raises(KeyError):
            content["not_exists_key"]

    def test_key_based_content_contains(self):
        content = DummyKeyBasedContent(
            key1=DummyContent(param="value1"),
            key2=DummyContent(param="value2"),
            default=DummyContent(param="default_value"),
        )
        assert "key1" in content
        assert "key2" in content
        assert "key3" not in content

    def test_key_based_content_no_contents(self):
        with pytest.raises(
            ValueError,
            match="At least one content must be specified.",
        ):
            DummyKeyBasedContent()
