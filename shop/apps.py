from django.apps import AppConfig


class ShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop'

    def ready(self):
        # Import signal handlers so they are registered on startup
        import shop.signals  # noqa: F401
