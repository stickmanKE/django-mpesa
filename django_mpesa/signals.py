from django.dispatch import Signal

# Fired after STK Push callback is received and processed.
# kwargs: transaction (STKPushTransaction), data (raw dict)
stk_push_callback = Signal()

# Fired after C2B payment is confirmed by Safaricom.
# kwargs: transaction (C2BTransaction), data (raw dict)
c2b_payment_received = Signal()

# Fired after B2C disbursement result is received.
# kwargs: transaction (B2CTransaction), data (raw dict)
b2c_result_received = Signal()
