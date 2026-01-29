"""
Smoke-check Classic Accounting integration.

Usage:
    python manage.py validate_accounting
"""

import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


REQUIRED_ENV_VARS = (
    "ACCOUNTING_DB_NAME",
    "ACCOUNTING_DB_USER",
    "ACCOUNTING_DB_PASSWORD",
    "ACCOUNTING_DB_HOST",
    "ACCOUNTING_DB_PORT",
)


class Command(BaseCommand):
    help = "Validate Classic Accounting integration setup"

    def handle(self, *args, **options):
        accounting_db = (settings.DATABASES or {}).get("accounting") or {}
        engine = accounting_db.get("ENGINE", "")

        # If we're not configured for the real Classic DB, fail fast and loud.
        if engine != "django.db.backends.postgresql":
            raise CommandError(
                "Classic Accounting DB is not configured. "
                "Set env vars: "
                + ", ".join(REQUIRED_ENV_VARS)
            )

        missing = [k for k in REQUIRED_ENV_VARS if not os.getenv(k)]
        if missing:
            raise CommandError(
                "Missing Classic Accounting env vars: " + ", ".join(missing)
            )

        # Try a minimal query against the external DB.
        from accounting_integration.models import ItmItems, Org

        try:
            _ = Org.objects.using("accounting").all()[:1].count()
            _ = ItmItems.objects.using("accounting").all()[:1].count()
        except Exception as e:
            raise CommandError(f"Unable to query Classic Accounting DB: {e}") from e

        self.stdout.write(self.style.SUCCESS("OK: Classic Accounting DB is reachable."))
