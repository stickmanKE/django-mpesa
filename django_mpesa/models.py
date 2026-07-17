import uuid
from django.db import models


class STKPushTransaction(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SUCCESS, 'Success'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=12)
    description = models.CharField(max_length=13)
    merchant_request_id = models.CharField(max_length=100, blank=True)
    checkout_request_id = models.CharField(max_length=100, blank=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    result_code = models.CharField(max_length=10, blank=True)
    result_description = models.TextField(blank=True)
    mpesa_receipt = models.CharField(max_length=50, blank=True)
    raw_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'STK Push Transaction'
        verbose_name_plural = 'STK Push Transactions'

    def __str__(self):
        return f"{self.phone} | KES {self.amount} | {self.get_status_display()}"

    @property
    def is_successful(self):
        return self.status == self.STATUS_SUCCESS


class C2BTransaction(models.Model):
    transaction_type = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=50, unique=True, db_index=True)
    transaction_time = models.CharField(max_length=20)
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2)
    business_short_code = models.CharField(max_length=10)
    bill_ref_number = models.CharField(max_length=50)
    invoice_number = models.CharField(max_length=50, blank=True)
    org_account_balance = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    third_party_transaction_id = models.CharField(max_length=50, blank=True)
    msisdn = models.CharField(max_length=15)
    first_name = models.CharField(max_length=50, blank=True)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    raw_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'C2B Transaction'
        verbose_name_plural = 'C2B Transactions'

    def __str__(self):
        return f"{self.msisdn} | KES {self.transaction_amount} | {self.transaction_id}"

    @property
    def full_name(self):
        parts = filter(None, [self.first_name, self.middle_name, self.last_name])
        return ' '.join(parts)


class B2CTransaction(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SUCCESS, 'Success'),
        (STATUS_FAILED, 'Failed'),
    ]

    conversation_id = models.CharField(max_length=100, blank=True, db_index=True)
    originator_conversation_id = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    remarks = models.CharField(max_length=100)
    command = models.CharField(max_length=30, default='BusinessPayment')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    result_code = models.CharField(max_length=10, blank=True)
    transaction_id = models.CharField(max_length=50, blank=True)
    transaction_completed_datetime = models.CharField(max_length=30, blank=True)
    receiver_party_public_name = models.CharField(max_length=100, blank=True)
    b2c_utility_account_balance = models.CharField(max_length=50, blank=True)
    raw_result = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'B2C Transaction'
        verbose_name_plural = 'B2C Transactions'

    def __str__(self):
        return f"{self.phone} | KES {self.amount} | {self.get_status_display()}"
