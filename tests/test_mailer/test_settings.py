import sys

import pytest
from pydantic import ValidationError

from aiogram_broadcaster.mailer.settings import DefaultMailerSettings, MailerSettings


class TestMailerSettings:
    def test_default_values(self):
        settings = MailerSettings()
        assert settings.interval == 0
        assert settings.run_on_startup is False
        assert settings.handle_retry_after is False
        assert settings.destroy_on_complete is False
        assert settings.disable_events is False
        assert settings.preserved is True
        assert settings.exclude_placeholders is None

    def test_invalid_interval(self):
        with pytest.raises(ValidationError):
            MailerSettings(interval=-1)


class TestDefaultMailerSettings:
    def test_default_values(self):
        settings = DefaultMailerSettings()
        assert settings.interval == 0
        assert settings.dynamic_interval is False
        assert settings.run_on_startup is False
        assert settings.handle_retry_after is False
        assert settings.destroy_on_complete is False
        assert settings.preserve is False

    def test_invalid_interval(self):
        with pytest.raises(
            ValueError,
            match="The interval must be greater than or equal to 0.",
        ):
            DefaultMailerSettings(interval=-1)

    def test_prepare_method(self):
        default_settings = DefaultMailerSettings(interval=5, dynamic_interval=True)
        prepared_settings = default_settings.prepare(run_on_startup=True, preserve=True)
        assert prepared_settings.interval == 5
        assert prepared_settings.dynamic_interval is True
        assert prepared_settings.run_on_startup is True
        assert prepared_settings.handle_retry_after is False
        assert prepared_settings.preserve is True
        assert prepared_settings.destroy_on_complete is False

    def test_prepare_method_without_args(self):
        default_settings = DefaultMailerSettings(interval=5, dynamic_interval=True, preserve=True)
        prepared_settings = default_settings.prepare()
        assert prepared_settings.interval == 5
        assert prepared_settings.dynamic_interval is True
        assert prepared_settings.run_on_startup is False
        assert prepared_settings.handle_retry_after is False
        assert prepared_settings.preserve is True
        assert prepared_settings.destroy_on_complete is False

    @pytest.mark.skipif(sys.version_info < (3, 12), reason="Requires Python 3.12 or higher.")
    def test_dataclass_params(self):
        dataclass_params = DefaultMailerSettings.__dataclass_params__
        assert dataclass_params.slots is True
        assert dataclass_params.kw_only is True
