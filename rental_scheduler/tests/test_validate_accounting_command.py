import pytest
from django.core.management import call_command
from django.core.management.base import CommandError


def test_validate_accounting_command_reports_missing_classic_env_vars(settings):
    """
    The smoke-check command should exist and fail loudly when Classic Accounting
    isn't configured, rather than silently attempting to query a placeholder DB.
    """
    # Force a non-Classic placeholder config, regardless of the developer's .env.
    settings.DATABASES["accounting"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }

    with pytest.raises(CommandError) as exc:
        call_command("validate_accounting")

    message = str(exc.value)
    assert "ACCOUNTING_DB_NAME" in message
