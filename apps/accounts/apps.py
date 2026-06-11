from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    verbose_name = "ERP Accounts"

    def ready(self):
        # Register signals when the app is fully loaded
        import apps.accounts.signals

        # Patch DRF FileField to return relative URLs instead of absolute ones
        from django.conf import settings
        from rest_framework.fields import FileField

        def to_representation(self, value):
            if not value:
                return None
            use_url = getattr(settings, "UPLOADED_FILES_USE_URL", True)
            if use_url:
                try:
                    return value.url
                except AttributeError:
                    return None
            return value.name

        FileField.to_representation = to_representation
