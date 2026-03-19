from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ("id", "transaction_type", "amount", "reference", "status", "created_at")
        read_only_fields = ("id", "reference", "status", "created_at")


class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=100)
    email = serializers.EmailField(required=False)


class WithdrawSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=100)
    bank_code = serializers.CharField(max_length=20)
    account_number = serializers.CharField(max_length=20)
    account_name = serializers.CharField(max_length=100)
