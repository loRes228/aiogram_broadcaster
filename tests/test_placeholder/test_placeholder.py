from aiogram_broadcaster.placeholder.placeholder import Placeholder


class TestPlaceholder:
    def test_initialization_with_value(self):
        value = "test_value"
        placeholder = Placeholder(key="test_key", value=value)
        assert placeholder.key == "test_key"
        assert placeholder.value == value

    def test_initialization_with_callable_value(self):
        async def mock_callback(**kwargs):
            pass

        placeholder = Placeholder(key="test_key", value=mock_callback)
        assert placeholder.key == "test_key"
        assert placeholder.value == mock_callback

    def test_hash(self):
        placeholder1 = Placeholder(key="key1", value="value1")
        placeholder2 = Placeholder(key="key2", value="value2")
        assert hash(placeholder1) != hash(placeholder2)

    def test_eq(self):
        placeholder1 = Placeholder(key="key1", value="value1")
        placeholder2 = Placeholder(key="key1", value="value2")
        placeholder3 = Placeholder(key="key2", value="value1")
        assert placeholder1 == placeholder2
        assert placeholder1 != placeholder3
        assert placeholder1 != "invalid_type"

    async def test_get_value_with_value(self):
        value = "test_value"
        placeholder = Placeholder(key="test_key", value=value)
        assert await placeholder.get_value() == value

    async def test_get_value_with_callable(self):
        async def mock_callback(**kwargs):
            return "callback_result"

        placeholder = Placeholder(key="test_key", value=mock_callback)
        result = await placeholder.get_value()
        assert result == "callback_result"
