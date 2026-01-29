import importlib


def test_accounting_integration_app_is_importable():
    importlib.import_module("accounting_integration")


def test_accounting_db_alias_is_configured(settings):
    assert "accounting" in settings.DATABASES


def test_accounting_db_router_is_configured(settings):
    assert "accounting_integration.router.AccountingRouter" in getattr(settings, "DATABASE_ROUTERS", [])


def test_accounting_router_routes_accounting_models_to_accounting_db():
    from accounting_integration.models import ItmItems, Org
    from accounting_integration.router import AccountingRouter

    router = AccountingRouter()

    assert router.db_for_read(Org) == "accounting"
    assert router.db_for_read(ItmItems) == "accounting"

    assert router.db_for_write(Org) == "accounting"
    assert router.db_for_write(ItmItems) == "accounting"


def test_accounting_router_disables_migrations_for_accounting_integration_app():
    from accounting_integration.router import AccountingRouter

    router = AccountingRouter()

    assert router.allow_migrate(db="default", app_label="accounting_integration") is False
    assert router.allow_migrate(db="accounting", app_label="accounting_integration") is False
