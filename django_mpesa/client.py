import base64
import logging
import requests
from datetime import datetime
from django.core.cache import cache

from .config import mpesa_config
from .exceptions import MpesaAuthError, MpesaRequestError, MpesaValidationError

logger = logging.getLogger('django_mpesa')


class MpesaClient:
    """
    Main client for interacting with Safaricom Daraja 2.0 API.

    Usage:
        from django_mpesa import mpesa

        resp = mpesa.stk_push(
            phone='0712345678',
            amount=100,
            reference='INV001',
            description='Payment for services',
        )
    """

    # ------------------------------------------------------------------ #
    # Auth                                                                 #
    # ------------------------------------------------------------------ #

    def _get_access_token(self) -> str:
        cached = cache.get(mpesa_config.TOKEN_CACHE_KEY)
        if cached:
            return cached

        url = f"{mpesa_config.base_url}/oauth/v1/generate?grant_type=client_credentials"
        credentials = base64.b64encode(
            f"{mpesa_config.CONSUMER_KEY}:{mpesa_config.CONSUMER_SECRET}".encode()
        ).decode()

        try:
            response = requests.get(
                url,
                headers={"Authorization": f"Basic {credentials}"},
                timeout=30,
            )
        except requests.RequestException as e:
            raise MpesaAuthError(f"Network error getting access token: {e}")

        if response.status_code != 200:
            raise MpesaAuthError(
                f"Failed to get access token (HTTP {response.status_code}): {response.text}"
            )

        token = response.json().get('access_token')
        if not token:
            raise MpesaAuthError("Empty access token received from Daraja")

        cache.set(mpesa_config.TOKEN_CACHE_KEY, token, mpesa_config.TOKEN_CACHE_TIMEOUT)
        logger.debug("M-Pesa access token refreshed and cached")
        return token

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json",
        }

    def _post(self, endpoint: str, payload: dict) -> dict:
        url = f"{mpesa_config.base_url}{endpoint}"
        logger.debug(f"POST {url} | payload keys: {list(payload.keys())}")

        try:
            response = requests.post(url, json=payload, headers=self._headers(), timeout=30)
        except requests.RequestException as e:
            raise MpesaRequestError(f"Network error: {e}")

        data = response.json()
        if response.status_code not in (200, 201):
            raise MpesaRequestError(
                data.get('errorMessage') or data.get('ResultDesc') or 'Request failed',
                response=data,
            )

        return data

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _timestamp(self) -> str:
        return datetime.now().strftime('%Y%m%d%H%M%S')

    def _stk_password(self) -> tuple[str, str]:
        ts = self._timestamp()
        raw = f"{mpesa_config.SHORTCODE}{mpesa_config.PASSKEY}{ts}"
        return base64.b64encode(raw.encode()).decode(), ts

    def normalize_phone(self, phone: str) -> str:
        """Convert any Kenyan phone format to 2547XXXXXXXX."""
        phone = str(phone).strip().replace(' ', '').replace('-', '').replace('+', '')
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        elif not phone.startswith('254'):
            phone = '254' + phone
        if len(phone) != 12:
            raise MpesaValidationError(
                f"Invalid phone number: '{phone}'. Expected 12-digit 2547XXXXXXXX format."
            )
        return phone

    # ------------------------------------------------------------------ #
    # STK Push (Lipa Na M-Pesa Online)                                    #
    # ------------------------------------------------------------------ #

    def stk_push(
        self,
        phone: str,
        amount: int | float,
        reference: str,
        description: str,
        callback_url: str = '',
        transaction_type: str = 'CustomerPayBillOnline',
    ) -> dict:
        """
        Trigger an STK Push prompt on the customer's phone.

        Args:
            phone: Customer phone (0712345678, +254712345678, 254712345678)
            amount: Amount in KES (integers only — fractions rounded)
            reference: Account reference shown on customer's phone (max 12 chars)
            description: Transaction description (max 13 chars)
            callback_url: Override default STK callback URL
            transaction_type: 'CustomerPayBillOnline' or 'CustomerBuyGoodsOnline'

        Returns:
            Daraja API response dict with MerchantRequestID, CheckoutRequestID, etc.
        """
        password, timestamp = self._stk_password()

        payload = {
            "BusinessShortCode": mpesa_config.SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": transaction_type,
            "Amount": int(amount),
            "PartyA": self.normalize_phone(phone),
            "PartyB": mpesa_config.SHORTCODE,
            "PhoneNumber": self.normalize_phone(phone),
            "CallBackURL": callback_url or mpesa_config.STK_CALLBACK_URL,
            "AccountReference": reference[:12],
            "TransactionDesc": description[:13],
        }
        return self._post('/mpesa/stkpush/v1/processrequest', payload)

    def stk_query(self, checkout_request_id: str) -> dict:
        """Query the status of an STK Push transaction."""
        password, timestamp = self._stk_password()
        payload = {
            "BusinessShortCode": mpesa_config.SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id,
        }
        return self._post('/mpesa/stkpushquery/v1/query', payload)

    # ------------------------------------------------------------------ #
    # C2B (Customer to Business — Paybill / Buy Goods)                    #
    # ------------------------------------------------------------------ #

    def c2b_register_urls(
        self,
        validation_url: str = '',
        confirmation_url: str = '',
        response_type: str = 'Completed',
    ) -> dict:
        """
        Register C2B callback URLs with Safaricom.
        Must be called once before going live (or after URL changes).

        Args:
            response_type: 'Completed' (auto-confirm) or 'Cancelled'
        """
        payload = {
            "ShortCode": mpesa_config.SHORTCODE,
            "ResponseType": response_type,
            "ConfirmationURL": confirmation_url or mpesa_config.C2B_CONFIRMATION_URL,
            "ValidationURL": validation_url or mpesa_config.C2B_VALIDATION_URL,
        }
        return self._post('/mpesa/c2b/v1/registerurl', payload)

    def c2b_simulate(self, phone: str, amount: int, bill_ref: str) -> dict:
        """Simulate a C2B payment — SANDBOX ONLY."""
        if not mpesa_config.is_sandbox:
            raise MpesaError("c2b_simulate is only available in sandbox environment")
        payload = {
            "ShortCode": mpesa_config.SHORTCODE,
            "CommandID": "CustomerPayBillOnline",
            "Amount": int(amount),
            "Msisdn": self.normalize_phone(phone),
            "BillRefNumber": bill_ref,
        }
        return self._post('/mpesa/c2b/v1/simulate', payload)

    # ------------------------------------------------------------------ #
    # B2C (Business to Customer — Disbursements)                          #
    # ------------------------------------------------------------------ #

    def b2c_payment(
        self,
        phone: str,
        amount: int | float,
        remarks: str,
        occasion: str = '',
        command: str = 'BusinessPayment',
        result_url: str = '',
        timeout_url: str = '',
    ) -> dict:
        """
        Send money from your shortcode to a customer (e.g. withdrawals, refunds).

        Args:
            command: 'BusinessPayment', 'SalaryPayment', or 'PromotionPayment'
        """
        payload = {
            "InitiatorName": mpesa_config.INITIATOR_NAME,
            "SecurityCredential": self._security_credential(),
            "CommandID": command,
            "Amount": int(amount),
            "PartyA": mpesa_config.B2C_SHORTCODE or mpesa_config.SHORTCODE,
            "PartyB": self.normalize_phone(phone),
            "Remarks": remarks[:100],
            "QueueTimeOutURL": timeout_url or mpesa_config.B2C_TIMEOUT_URL,
            "ResultURL": result_url or mpesa_config.B2C_RESULT_URL,
            "Occasion": occasion,
        }
        return self._post('/mpesa/b2c/v1/paymentrequest', payload)

    def _security_credential(self) -> str:
        """
        Encrypts initiator password with Safaricom's public certificate.
        For production, use the production certificate from Daraja portal.
        See docs/security_credential.md for the full production setup.
        """
        # Simplified for sandbox — production requires RSA encryption
        # with Safaricom's certificate. See docs for production usage.
        return base64.b64encode(mpesa_config.INITIATOR_PASSWORD.encode()).decode()


mpesa = MpesaClient()
