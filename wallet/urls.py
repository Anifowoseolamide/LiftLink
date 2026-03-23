from django.urls import path
from .views import WalletHistoryView, DepositView, WithdrawView, PaystackWebhookView, MockDepositView, WalletBalanceView

urlpatterns = [
    path("balance/", WalletBalanceView.as_view(), name="wallet-balance"),
    path("history/", WalletHistoryView.as_view(), name="wallet-history"),
    path("deposit/", DepositView.as_view(), name="wallet-deposit"),
    path("withdraw/", WithdrawView.as_view(), name="wallet-withdraw"),
    path("paystack-webhook/", PaystackWebhookView.as_view(), name="paystack-webhook"),
    path("mock-deposit/", MockDepositView.as_view(), name="mock-deposit"),
]
