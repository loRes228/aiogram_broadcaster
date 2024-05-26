import pytest

from aiogram_broadcaster.contents.base import BaseContent
from aiogram_broadcaster.contents.key_based import KeyBasedContent


class MyContent(BaseContent, register=False):
    some_field: str = "test"

    async def __call__(self):
        return "my content result"


class MyKeyBasedContent(KeyBasedContent, register=False):
    async def __call__(self):
        return "test_key"


class TestKeyBasedContent:
    def test_init_without_args(self):
        with pytest.raises(
            ValueError,
            match="At least one content must be specified.",
        ):
            MyKeyBasedContent()

    def test_init_only_extra(self):
        MyKeyBasedContent(foo=MyContent())

    def test_init_only_default(self):
        MyKeyBasedContent(default=MyContent())

    def test_init(self):
        foo = MyContent()
        bar = MyContent()
        content = MyKeyBasedContent(foo=foo, bar=bar)
        assert foo == content["foo"] == content.__pydantic_extra__["foo"]
        assert bar == content["bar"] == content.__pydantic_extra__["bar"]
        assert "foo" in content
        assert "bar" in content
        assert "baz" not in content

    def test_init_with_default(self):
        default = MyContent()
        foo = MyContent()
        content = MyKeyBasedContent(default=default, foo=foo)
        assert foo == content["foo"] == content.__pydantic_extra__["foo"]
        assert content["bar"] == default
        assert "bar" not in content.__pydantic_extra__
        assert "foo" in content
        assert "bar" not in content

    async def test_as_method(self):
        content = MyKeyBasedContent(default=MyContent())
        assert await content.as_method() == "my content result"
