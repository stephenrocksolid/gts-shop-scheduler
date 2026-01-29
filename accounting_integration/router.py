"""
Database router for directing accounting_integration queries to the accounting database.
"""


class AccountingRouter:
    """
    A router to control all database operations on models in the
    accounting_integration application.
    """

    route_app_labels = {"accounting_integration"}

    def db_for_read(self, model, **hints):
        """
        Attempts to read accounting_integration models go to accounting db.
        """
        if model._meta.app_label in self.route_app_labels:
            return "accounting"
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write accounting_integration models go to accounting db.
        """
        if model._meta.app_label in self.route_app_labels:
            return "accounting"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the accounting_integration app is involved.
        """
        if (
            obj1._meta.app_label in self.route_app_labels
            or obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Prevent all migrations on the accounting database - it's an external system.
        Also prevent accounting_integration from being migrated on any database.
        """
        # Never allow migrations on the accounting database (it's managed externally)
        if db == "accounting":
            return False

        # Never allow accounting_integration app to be migrated anywhere
        if app_label in self.route_app_labels:
            return False

        # All other apps can migrate on other databases (default, etc.)
        return None

