default_app_config = 'django_mpesa.apps.DjangoMpesaConfig'
from .client import mpesa  # noqa: F401
__all__ = ['mpesa']
