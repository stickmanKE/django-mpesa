SECRET_KEY = 'test-secret-key-for-django-mpesa'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django_mpesa',
]
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
MPESA_CONFIG = {
    'CONSUMER_KEY': 'test_key',
    'CONSUMER_SECRET': 'test_secret',
    'SHORTCODE': '174379',
    'PASSKEY': 'test_passkey',
    'ENVIRONMENT': 'sandbox',
    'STK_CALLBACK_URL': 'https://example.com/mpesa/stk/callback/',
    'C2B_CONFIRMATION_URL': 'https://example.com/mpesa/c2b/confirmation/',
    'C2B_VALIDATION_URL': 'https://example.com/mpesa/c2b/validation/',
    'B2C_RESULT_URL': 'https://example.com/mpesa/b2c/result/',
    'B2C_TIMEOUT_URL': 'https://example.com/mpesa/b2c/timeout/',
}
