from django.conf import settings


DEFAULTS = {
    'CONSUMER_KEY': '',
    'CONSUMER_SECRET': '',
    'SHORTCODE': '',
    'PASSKEY': '',
    'ENVIRONMENT': 'sandbox',           # 'sandbox' or 'production'
    'INITIATOR_NAME': '',
    'INITIATOR_PASSWORD': '',
    'B2C_SHORTCODE': '',
    'STK_CALLBACK_URL': '',
    'C2B_VALIDATION_URL': '',
    'C2B_CONFIRMATION_URL': '',
    'B2C_RESULT_URL': '',
    'B2C_TIMEOUT_URL': '',
    'TOKEN_CACHE_KEY': 'mpesa_access_token',
    'TOKEN_CACHE_TIMEOUT': 3500,        # seconds (token expires at 3600)
}


class MpesaConfig:
    def __init__(self):
        self._settings = getattr(settings, 'MPESA_CONFIG', {})

    def __getattr__(self, key):
        if key.startswith('_'):
            raise AttributeError(key)
        if key in DEFAULTS:
            return self._settings.get(key, DEFAULTS[key])
        raise AttributeError(f"Invalid MPESA_CONFIG key: '{key}'")

    @property
    def base_url(self):
        if self.ENVIRONMENT == 'production':
            return 'https://api.safaricom.co.ke'
        return 'https://sandbox.safaricom.co.ke'

    @property
    def is_sandbox(self):
        return self.ENVIRONMENT != 'production'


mpesa_config = MpesaConfig()
