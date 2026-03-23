from rest_framework import serializers
from .models import Transaction


TRANSACTION_DESCRIPTIONS = {
    Transaction.DEPOSIT: "Wallet Top-up",
    Transaction.WITHDRAW: "Withdrawal",
    Transaction.ESCROW: "Ride Booking (Held)",
    Transaction.RELEASE: "Ride Earnings Released",
    Transaction.REFUND: "Booking Refund",
}


class TransactionSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ("id", "transaction_type", "description", "amount", "reference", "status", "created_at", "meta")
        read_only_fields = ("id", "reference", "status", "created_at", "meta")

    def get_description(self, obj):
        return TRANSACTION_DESCRIPTIONS.get(obj.transaction_type, obj.transaction_type)


class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=100)
    email = serializers.EmailField(required=False)


class WithdrawSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=100)
    bank_code = serializers.CharField(max_length=20)
    account_number = serializers.CharField(max_length=20)
    account_name = serializers.CharField(max_length=100)
