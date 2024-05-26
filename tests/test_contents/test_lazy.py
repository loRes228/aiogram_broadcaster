import unittest.mock

import pytest

from aiogram_broadcaster.contents.base import BaseContent
from aiogram_broadcaster.contents.lazy import LazyContent


class MyContent(BaseContent, register=False):
    some_field: str = "test"

    async def __call__(self):
        return "content result"


class MyLazyContent(LazyContent, register=False, frozen=False):
    async def __call__(self):
        return MyContent()


class TestLazyContent:
    async def test_as_method(self):
        content = MyLazyContent()
        assert await content.as_method() == "content result"

    async def test_as_method_calls_callback(self):
        content = MyLazyContent()
        with unittest.mock.patch.object(
            target=content._callback,
            attribute="call",
            new_callable=unittest.mock.AsyncMock,
            return_value=MyContent(),
        ) as mocked_callback:
            await content.as_method(test_param=1)
            mocked_callback.assert_called_once_with(content, test_param=1)

    async def test_as_method_invalid_type(self):
        content = MyLazyContent()
        with unittest.mock.patch.object(
            target=content._callback,
            attribute="call",
            return_value="invalid type",
        ), pytest.raises(
            TypeError,
            match=(
                "The MyLazyContent expected to return an content of "
                "type BaseContent, not a str."
            ),
        ):
            await content.as_method()
