from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    Configuration class for the `accounts` app.

    Attributes:
    - `default_auto_field`: Specifies the default field type for primary keys in models.
    - `name`: The name of the app, used by Django to identify it.
    """
    default_auto_field = "django.db.models.BigAutoField"  # Default primary key field type
    name = "accounts"  # App name
