from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    verbose_name = "ERP Accounts"

    def ready(self):
        # Register signals when the app is fully loaded
        import apps.accounts.signals
