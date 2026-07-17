import pytest
from unittest.mock import patch, MagicMock
from django_mpesa.client import MpesaClient
from django_mpesa.exceptions import MpesaValidationError


@pytest.fixture
def client():
    return MpesaClient()


class TestNormalizePhone:
    def test_local_format(self, client):
        assert client.normalize_phone('0712345678') == '254712345678'

    def test_international_format(self, client):
        assert client.normalize_phone('+254712345678') == '254712345678'

    def test_already_normalized(self, client):
        assert client.normalize_phone('254712345678') == '254712345678'

    def test_with_spaces(self, client):
        assert client.normalize_phone('0712 345 678') == '254712345678'

    def test_invalid_raises(self, client):
        with pytest.raises(MpesaValidationError):
            client.normalize_phone('07123')  # too short


class TestSTKPush:
    @patch('django_mpesa.client.MpesaClient._get_access_token', return_value='test_token')
    @patch('django_mpesa.client.requests.post')
    def test_stk_push_success(self, mock_post, mock_token, client):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                'MerchantRequestID': 'test-123',
                'CheckoutRequestID': 'ws_CO_test',
                'ResponseCode': '0',
                'ResponseDescription': 'Success',
            }
        )
        with patch('django_mpesa.config.mpesa_config.SHORTCODE', '174379'), \
             patch('django_mpesa.config.mpesa_config.PASSKEY', 'testpasskey'), \
             patch('django_mpesa.config.mpesa_config.STK_CALLBACK_URL', 'https://example.com/callback'):
            result = client.stk_push(
                phone='0712345678',
                amount=100,
                reference='INV001',
                description='Test payment',
            )
        assert 'MerchantRequestID' in result
