from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='STKPushTransaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('phone', models.CharField(max_length=15)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('reference', models.CharField(max_length=12)),
                ('description', models.CharField(max_length=13)),
                ('merchant_request_id', models.CharField(blank=True, max_length=100)),
                ('checkout_request_id', models.CharField(blank=True, db_index=True, max_length=100)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('result_code', models.CharField(blank=True, max_length=10)),
                ('result_description', models.TextField(blank=True)),
                ('mpesa_receipt', models.CharField(blank=True, max_length=50)),
                ('raw_response', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['-created_at'], 'verbose_name': 'STK Push Transaction'},
        ),
        migrations.CreateModel(
            name='C2BTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('transaction_type', models.CharField(max_length=50)),
                ('transaction_id', models.CharField(db_index=True, max_length=50, unique=True)),
                ('transaction_time', models.CharField(max_length=20)),
                ('transaction_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('business_short_code', models.CharField(max_length=10)),
                ('bill_ref_number', models.CharField(max_length=50)),
                ('invoice_number', models.CharField(blank=True, max_length=50)),
                ('org_account_balance', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('third_party_transaction_id', models.CharField(blank=True, max_length=50)),
                ('msisdn', models.CharField(max_length=15)),
                ('first_name', models.CharField(blank=True, max_length=50)),
                ('middle_name', models.CharField(blank=True, max_length=50)),
                ('last_name', models.CharField(blank=True, max_length=50)),
                ('raw_data', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-created_at'], 'verbose_name': 'C2B Transaction'},
        ),
        migrations.CreateModel(
            name='B2CTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('conversation_id', models.CharField(blank=True, db_index=True, max_length=100)),
                ('originator_conversation_id', models.CharField(blank=True, max_length=100)),
                ('phone', models.CharField(max_length=15)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('remarks', models.CharField(max_length=100)),
                ('command', models.CharField(default='BusinessPayment', max_length=30)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('result_code', models.CharField(blank=True, max_length=10)),
                ('transaction_id', models.CharField(blank=True, max_length=50)),
                ('transaction_completed_datetime', models.CharField(blank=True, max_length=30)),
                ('receiver_party_public_name', models.CharField(blank=True, max_length=100)),
                ('b2c_utility_account_balance', models.CharField(blank=True, max_length=50)),
                ('raw_result', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['-created_at'], 'verbose_name': 'B2C Transaction'},
        ),
    ]
