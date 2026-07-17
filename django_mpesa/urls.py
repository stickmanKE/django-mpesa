from django.urls import path
from .views import (
    STKPushCallbackView,
    C2BValidationView,
    C2BConfirmationView,
    B2CResultView,
    B2CTimeoutView,
)

app_name = 'mpesa'

urlpatterns = [
    path('stk/callback/', STKPushCallbackView.as_view(), name='stk-callback'),
    path('c2b/validation/', C2BValidationView.as_view(), name='c2b-validation'),
    path('c2b/confirmation/', C2BConfirmationView.as_view(), name='c2b-confirmation'),
    path('b2c/result/', B2CResultView.as_view(), name='b2c-result'),
    path('b2c/timeout/', B2CTimeoutView.as_view(), name='b2c-timeout'),
]
