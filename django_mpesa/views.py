import json
import logging

from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import STKPushTransaction, C2BTransaction, B2CTransaction
from .signals import stk_push_callback, c2b_payment_received, b2c_result_received

logger = logging.getLogger('django_mpesa')

OK_RESPONSE = {"ResultCode": 0, "ResultDesc": "Accepted"}


def _safe_decode(request):
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logger.warning(f"M-Pesa callback body decode error: {e}")
        return None


@method_decorator(csrf_exempt, name='dispatch')
class STKPushCallbackView(View):
    """
    Handles STK Push payment callbacks from Safaricom.
    URL: /mpesa/stk/callback/

    Connect to your own logic via signals:
        from django_mpesa.signals import stk_push_callback

        @receiver(stk_push_callback)
        def handle_stk(sender, transaction, data, **kwargs):
            if transaction.is_successful:
                activate_user_account(transaction)
    """

    def post(self, request, *args, **kwargs):
        data = _safe_decode(request)
        if not data:
            return JsonResponse(OK_RESPONSE)

        try:
            body = data.get('Body', {}).get('stkCallback', {})
            checkout_request_id = body.get('CheckoutRequestID', '')
            result_code = str(body.get('ResultCode', ''))
            result_desc = body.get('ResultDesc', '')

            tx = STKPushTransaction.objects.filter(
                checkout_request_id=checkout_request_id
            ).first()

            if not tx:
                logger.warning(f"STK callback for unknown CheckoutRequestID: {checkout_request_id}")
                return JsonResponse(OK_RESPONSE)

            tx.result_code = result_code
            tx.result_description = result_desc
            tx.raw_response = data

            if result_code == '0':
                tx.status = STKPushTransaction.STATUS_SUCCESS
                for item in body.get('CallbackMetadata', {}).get('Item', []):
                    if item.get('Name') == 'MpesaReceiptNumber':
                        tx.mpesa_receipt = item.get('Value', '')
                        break
            else:
                tx.status = STKPushTransaction.STATUS_FAILED

            tx.save(update_fields=['status', 'result_code', 'result_description',
                                   'mpesa_receipt', 'raw_response', 'updated_at'])

            stk_push_callback.send(sender=STKPushTransaction, transaction=tx, data=data)
            logger.info(f"STK callback processed: {tx}")

        except Exception as e:
            logger.exception(f"STK callback processing error: {e}")

        return JsonResponse(OK_RESPONSE)


@method_decorator(csrf_exempt, name='dispatch')
class C2BValidationView(View):
    """
    Validates incoming C2B payments before confirmation.
    Override to add custom business logic (e.g. validate account numbers).

    To reject a payment, return ResultCode: C2001 with a reason.
    """

    def post(self, request, *args, **kwargs):
        # Default: accept all payments. Subclass to customise.
        return JsonResponse(OK_RESPONSE)


@method_decorator(csrf_exempt, name='dispatch')
class C2BConfirmationView(View):
    """
    Records confirmed C2B payments from Safaricom.
    URL: /mpesa/c2b/confirmation/
    """

    def post(self, request, *args, **kwargs):
        data = _safe_decode(request)
        if not data:
            return JsonResponse(OK_RESPONSE)

        try:
            tx, created = C2BTransaction.objects.get_or_create(
                transaction_id=data.get('TransID', ''),
                defaults={
                    'transaction_type': data.get('TransactionType', ''),
                    'transaction_time': data.get('TransTime', ''),
                    'transaction_amount': data.get('TransAmount', 0),
                    'business_short_code': data.get('BusinessShortCode', ''),
                    'bill_ref_number': data.get('BillRefNumber', ''),
                    'invoice_number': data.get('InvoiceNumber', ''),
                    'msisdn': data.get('MSISDN', ''),
                    'first_name': data.get('FirstName', ''),
                    'middle_name': data.get('MiddleName', ''),
                    'last_name': data.get('LastName', ''),
                    'raw_data': data,
                }
            )
            if created:
                c2b_payment_received.send(
                    sender=C2BTransaction, transaction=tx, data=data
                )
                logger.info(f"C2B payment confirmed: {tx}")
        except Exception as e:
            logger.exception(f"C2B confirmation error: {e}")

        return JsonResponse(OK_RESPONSE)


@method_decorator(csrf_exempt, name='dispatch')
class B2CResultView(View):
    """Handles B2C disbursement results from Safaricom."""

    def post(self, request, *args, **kwargs):
        data = _safe_decode(request)
        if not data:
            return JsonResponse(OK_RESPONSE)

        try:
            result = data.get('Result', {})
            params = {
                item.get('Key'): item.get('Value')
                for item in result.get('ResultParameters', {}).get('ResultParameter', [])
            }

            tx = B2CTransaction.objects.filter(
                conversation_id=result.get('ConversationID', '')
            ).first()

            if tx:
                result_code = str(result.get('ResultCode', '1'))
                tx.result_code = result_code
                tx.status = (B2CTransaction.STATUS_SUCCESS
                             if result_code == '0' else B2CTransaction.STATUS_FAILED)
                tx.transaction_id = str(params.get('TransactionID', ''))
                tx.transaction_completed_datetime = str(
                    params.get('TransactionCompletedDateTime', '')
                )
                tx.receiver_party_public_name = str(
                    params.get('ReceiverPartyPublicName', '')
                )
                tx.b2c_utility_account_balance = str(
                    params.get('B2CUtilityAccountAvailableFunds', '')
                )
                tx.raw_result = data
                tx.save()
                b2c_result_received.send(
                    sender=B2CTransaction, transaction=tx, data=data
                )
                logger.info(f"B2C result received: {tx}")
        except Exception as e:
            logger.exception(f"B2C result processing error: {e}")

        return JsonResponse(OK_RESPONSE)


@method_decorator(csrf_exempt, name='dispatch')
class B2CTimeoutView(View):
    """Handles B2C queue timeout callbacks."""

    def post(self, request, *args, **kwargs):
        data = _safe_decode(request)
        if data:
            logger.warning(f"B2C timeout received: {data}")
        return JsonResponse(OK_RESPONSE)
