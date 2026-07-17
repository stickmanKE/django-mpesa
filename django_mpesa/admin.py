from django.contrib import admin
from .models import STKPushTransaction, C2BTransaction, B2CTransaction


@admin.register(STKPushTransaction)
class STKPushTransactionAdmin(admin.ModelAdmin):
    list_display = ['phone', 'amount', 'reference', 'status', 'mpesa_receipt', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['phone', 'reference', 'mpesa_receipt', 'checkout_request_id']
    readonly_fields = ['id', 'merchant_request_id', 'checkout_request_id',
                       'raw_response', 'created_at', 'updated_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'


@admin.register(C2BTransaction)
class C2BTransactionAdmin(admin.ModelAdmin):
    list_display = ['msisdn', 'full_name', 'transaction_amount',
                    'bill_ref_number', 'transaction_id', 'created_at']
    list_filter = ['created_at']
    search_fields = ['msisdn', 'transaction_id', 'bill_ref_number']
    readonly_fields = ['raw_data', 'created_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Name'


@admin.register(B2CTransaction)
class B2CTransactionAdmin(admin.ModelAdmin):
    list_display = ['phone', 'amount', 'status', 'transaction_id', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['phone', 'transaction_id', 'conversation_id']
    readonly_fields = ['raw_result', 'created_at', 'updated_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
