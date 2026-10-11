# Django-Mpesa Wrapper

> The most complete M-Pesa Daraja 2.0 integration for Django. STK Push, C2B, B2C — batteries included.

[![PyPI version](https://badge.fury.io/py/django-mpesa.svg)](https://badge.fury.io/py/django-mpesa)
[![Django Versions](https://img.shields.io/badge/Django-3.2%20%7C%204.x%20%7C%205.x-green)](https://www.djangoproject.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Built and maintained by [stickmanKE](https://github.com/stickmanKE) • [Hire me for M-Pesa integration →](mailto:bunifulab@gmail.com)

---

## Features

- ✅ **STK Push** (Lipa Na M-Pesa Online) — with automatic callback handling
- ✅ **STK Query** — check payment status anytime
- ✅ **C2B** (Paybill / Buy Goods) — URL registration + confirmation
- ✅ **B2C** (Disbursements) — send money to customers/withdrawals
- ✅ **Django Signals** — hook into payment events without modifying library code
- ✅ **Django Admin** — view all transactions out of the box
- ✅ **Token caching** — automatic OAuth token refresh using Django cache
- ✅ **Phone normalisation** — accepts `07xx`, `+254xx`, `254xx`
- ✅ **Full test suite** — pytest with Django

---

## Installation

```bash
pip install django-mpesa
```

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'django_mpesa',
]
```

Include URLs:

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    ...
    path('mpesa/', include('django_mpesa.urls', namespace='mpesa')),
]
```

Run migrations:

```bash
python manage.py migrate
```

---

## Configuration

Add to your `settings.py`:

```python
MPESA_CONFIG = {
    # Daraja credentials (from developer.safaricom.co.ke)
    'CONSUMER_KEY': 'your_consumer_key',
    'CONSUMER_SECRET': 'your_consumer_secret',

    # STK Push / C2B settings
    'SHORTCODE': '174379',          # Your paybill or till number
    'PASSKEY': 'your_lipa_na_mpesa_passkey',

    # 'sandbox' or 'production'
    'ENVIRONMENT': 'sandbox',

    # B2C settings (disbursements)
    'INITIATOR_NAME': 'your_initiator_name',
    'INITIATOR_PASSWORD': 'your_initiator_password',
    'B2C_SHORTCODE': '600000',      # Usually same as SHORTCODE

    # Callback URLs (must be HTTPS and publicly reachable)
    'STK_CALLBACK_URL': 'https://yourdomain.com/mpesa/stk/callback/',
    'C2B_VALIDATION_URL': 'https://yourdomain.com/mpesa/c2b/validation/',
    'C2B_CONFIRMATION_URL': 'https://yourdomain.com/mpesa/c2b/confirmation/',
    'B2C_RESULT_URL': 'https://yourdomain.com/mpesa/b2c/result/',
    'B2C_TIMEOUT_URL': 'https://yourdomain.com/mpesa/b2c/timeout/',
}
```

> **Tip for local development:** Use [ngrok](https://ngrok.com) or [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/) to expose your local server for callbacks.

---

## Usage

### STK Push

```python
from django_mpesa import mpesa
from django_mpesa.models import STKPushTransaction

# Trigger payment prompt
response = mpesa.stk_push(
    phone='0712345678',
    amount=500,
    reference='INV001',
    description='Order payment',
)

# Save to DB for tracking
STKPushTransaction.objects.create(
    phone='0712345678',
    amount=500,
    reference='INV001',
    description='Order payment',
    merchant_request_id=response['MerchantRequestID'],
    checkout_request_id=response['CheckoutRequestID'],
)
```

### Listen for Payment Confirmation

```python
# myapp/signals.py
from django.dispatch import receiver
from django_mpesa.signals import stk_push_callback
from django_mpesa.models import STKPushTransaction

@receiver(stk_push_callback, sender=STKPushTransaction)
def on_payment_complete(sender, transaction, data, **kwargs):
    if transaction.is_successful:
        # Activate subscription, fulfil order, top up credits, etc.
        activate_order(transaction.reference)
    else:
        notify_user_payment_failed(transaction.phone)
```

### C2B — Register URLs (run once)

```python
from django_mpesa import mpesa

mpesa.c2b_register_urls()
# URLs from settings are registered automatically
```

### B2C — Send Money (Withdrawals / Refunds)

```python
from django_mpesa import mpesa
from django_mpesa.models import B2CTransaction

response = mpesa.b2c_payment(
    phone='0712345678',
    amount=200,
    remarks='Wallet withdrawal',
    command='BusinessPayment',  # or 'SalaryPayment', 'PromotionPayment'
)

B2CTransaction.objects.create(
    phone='0712345678',
    amount=200,
    remarks='Wallet withdrawal',
    conversation_id=response.get('ConversationID', ''),
    originator_conversation_id=response.get('OriginatorConversationID', ''),
)
```

---

## Callback URLs

| URL | Purpose |
|-----|---------|
| `/mpesa/stk/callback/` | STK Push result |
| `/mpesa/c2b/validation/` | C2B validation (optional) |
| `/mpesa/c2b/confirmation/` | C2B confirmation |
| `/mpesa/b2c/result/` | B2C result |
| `/mpesa/b2c/timeout/` | B2C queue timeout |

---

## Running Tests

```bash
pip install pytest pytest-django
pytest
```

---

## Changelog

### 1.0.0
- Initial release
- STK Push, C2B, B2C support
- Django Signals for all events
- Full Django Admin integration
- Automatic phone number normalization

---

## License

MIT © [stickmanKE](https://github.com/stickmanKE)
