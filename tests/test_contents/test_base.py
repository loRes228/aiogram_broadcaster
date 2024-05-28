import re

import pytest
from pydantic import ValidationError

from aiogram_broadcaster.contents.base import VALIDATOR_KEY, BaseContent


class DummyContent(BaseContent, register=False):
    async def __call__(self, **kwargs):
        return {"method": "dummy_method", **kwargs}


class TestBaseContent:
    def test_registration(self):
        assert not DummyContent.is_registered()
        DummyContent.register()
        assert DummyContent.is_registered()
        DummyContent.unregister()
        assert not DummyContent.is_registered()
        with pytest.raises(
            TypeError,
            match="BaseContent cannot be registered.",
        ):
            BaseContent.register()

    def test_validate_invalid_type(self):
        with pytest.raises(ValidationError):
            BaseContent.model_validate(object())

    def test_double_registration(self):
        DummyContent.register()
        with pytest.raises(
            RuntimeError,
            match="The content 'DummyContent' is already registered.",
        ):
            DummyContent.register()
        DummyContent.unregister()

    def test_unregister_non_registered(self):
        with pytest.raises(
            RuntimeError,
            match="The content 'DummyContent' is not registered.",
        ):
            DummyContent.unregister()

    async def test_callable(self):
        content = DummyContent()
        result = await content(param="value")
        assert result == {"method": "dummy_method", "param": "value"}

    async def test_as_method(self):
        content = DummyContent()
        result = await content.as_method(param="value")
        assert result == {"method": "dummy_method", "param": "value"}

    def test_validation(self):
        DummyContent.register()
        valid_data = {VALIDATOR_KEY: "DummyContent", "param": "value"}
        content = DummyContent.model_validate(valid_data)
        assert content.param == "value"

        invalid_data = {VALIDATOR_KEY: "NonExistentContent", "param": "value"}
        with pytest.raises(
            ValidationError,
            match=re.escape(
                "Content 'NonExistentContent' has not been registered, "
                "you can register using the 'NonExistentContent.register()' method.",
            ),
        ):
            BaseContent.model_validate(invalid_data)
        DummyContent.unregister()

    def test_serialization(self):
        content = DummyContent(param="value")
        serialized = content.model_dump()
        assert serialized[VALIDATOR_KEY] == "DummyContent"
        assert serialized["param"] == "value"
