import json
import pytest
from django.test import TestCase, RequestFactory
from django_mpesa.views import STKPushCallbackView, C2BConfirmationView
from django_mpesa.models import STKPushTransaction, C2BTransaction


class TestSTKCallback(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.tx = STKPushTransaction.objects.create(
            phone='254712345678',
            amount=100,
            reference='INV001',
            description='Test',
            checkout_request_id='ws_CO_test123',
        )

    def _make_request(self, payload):
        return self.factory.post(
            '/mpesa/stk/callback/',
            data=json.dumps(payload),
            content_type='application/json',
        )

    def test_successful_callback(self):
        payload = {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": "test",
                    "CheckoutRequestID": "ws_CO_test123",
                    "ResultCode": 0,
                    "ResultDesc": "The service request is processed successfully.",
                    "CallbackMetadata": {
                        "Item": [
                            {"Name": "Amount", "Value": 100},
                            {"Name": "MpesaReceiptNumber", "Value": "LGR7IRYKKL"},
                            {"Name": "PhoneNumber", "Value": 254712345678},
                        ]
                    }
                }
            }
        }
        request = self._make_request(payload)
        response = STKPushCallbackView.as_view()(request)
        assert response.status_code == 200
        self.tx.refresh_from_db()
        assert self.tx.status == 'success'
        assert self.tx.mpesa_receipt == 'LGR7IRYKKL'

    def test_failed_callback(self):
        payload = {
            "Body": {
                "stkCallback": {
                    "CheckoutRequestID": "ws_CO_test123",
                    "ResultCode": 1032,
                    "ResultDesc": "Request cancelled by user",
                }
            }
        }
        request = self._make_request(payload)
        STKPushCallbackView.as_view()(request)
        self.tx.refresh_from_db()
        assert self.tx.status == 'failed'
