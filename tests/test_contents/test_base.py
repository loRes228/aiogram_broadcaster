import re
import unittest.mock

import pydantic
import pytest

from aiogram_broadcaster.contents.base import VALIDATOR_KEY, BaseContent


class TestBaseContent:
    def test_register_and_unregister(self):
        with pytest.raises(
            TypeError,
            match="BaseContent cannot be registered.",
        ):
            BaseContent.register()

        class RegisteredContent(BaseContent):
            pass

        class UnregisteredContent(BaseContent, register=False):
            pass

        assert RegisteredContent.is_registered()
        RegisteredContent.unregister()
        assert not RegisteredContent.is_registered()

        with pytest.raises(
            RuntimeError,
            match="The content 'RegisteredContent' is not registered.",
        ):
            RegisteredContent.unregister()

        assert not UnregisteredContent.is_registered()
        UnregisteredContent.register()
        assert UnregisteredContent.is_registered()

        with pytest.raises(
            RuntimeError,
            match="The content 'UnregisteredContent' is already registered.",
        ):
            UnregisteredContent.register()

        UnregisteredContent.unregister()

    async def test_as_method(self):
        MOCK_RESULT = unittest.mock.sentinel.RESULT

        class MyContent(BaseContent, register=False):
            async def __call__(self, test_param):
                MOCK_RESULT.test_param = test_param
                return MOCK_RESULT

        content = MyContent()
        result = await content.as_method(test_param=1)
        assert result is MOCK_RESULT
        assert result.test_param == 1

    async def test_as_method_calls_callback(self):
        class MyContent(BaseContent, register=False, frozen=False):
            async def __call__(self, **kwargs):
                return

        content = MyContent()
        with unittest.mock.patch.object(
            target=MyContent,
            attribute="_callback",
            new_callable=unittest.mock.AsyncMock,
        ) as mocked_callback:
            await content.as_method(test_param=1)
            mocked_callback.call.assert_called_once_with(content, test_param=1)

    def test_serialization(self):
        class MyContent(BaseContent, register=False):
            some_field: str

            async def __call__(self):
                return

        content = MyContent(some_field="test")
        serialized = content.model_dump()
        assert serialized[VALIDATOR_KEY] == "MyContent"
        assert serialized["some_field"] == "test"

    def test_validation(self):
        class MyContent(BaseContent, register=True):
            some_field: str

            async def __call__(self):
                return

        with pytest.raises(pydantic.ValidationError):
            BaseContent.model_validate(object())

        with pytest.raises(
            ValueError,
            match=re.escape(
                "Content 'NotExistsContent' has not been registered, "
                "you can register using the 'NotExistsContent.register()' method.",
            ),
        ):
            BaseContent.model_validate({VALIDATOR_KEY: "NotExistsContent", "some_field": "test"})

        validated_content = BaseContent.model_validate({
            VALIDATOR_KEY: "MyContent",
            "some_field": "test",
        })
        assert isinstance(validated_content, MyContent)
        assert validated_content.some_field == "test"

        MyContent.unregister()
