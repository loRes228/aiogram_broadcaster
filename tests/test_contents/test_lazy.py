import pytest

from aiogram_broadcaster.contents.base import BaseContent
from aiogram_broadcaster.contents.lazy import LazyContent


class DummyContent(BaseContent, register=False):
    async def __call__(self, **kwargs):
        return {
            "method": "dummy_method",
            **kwargs,
            **(self.model_extra or {}),
        }


class DummyLazyContent(LazyContent, register=False):
    async def __call__(self, **kwargs):
        return DummyContent(param="value")


class TestLazyContent:
    async def test_lazy_content_as_method(self):
        content = DummyLazyContent()
        result = await content.as_method(context_param="context_value")
        assert isinstance(result, dict)
        assert result == {
            "method": "dummy_method",
            "param": "value",
            "context_param": "context_value",
        }

    async def test_lazy_content_as_method_invalid_return(self):
        class InvalidLazyContent(LazyContent):
            async def __call__(self, **kwargs):
                return "not_a_base_content"

        content = InvalidLazyContent()
        with pytest.raises(
            TypeError,
            match="The 'InvalidLazyContent' expected to return an content of "
            "type BaseContent, not a str.",
        ):
            await content.as_method(context_param="context_value")
