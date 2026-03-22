import uuid
import decimal
import hashlib
import hmac
import json
import requests

from django.conf import settings
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Transaction
from .serializers import TransactionSerializer, DepositSerializer, WithdrawSerializer


def _paystack_headers():
    return {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }


class WalletHistoryView(generics.ListAPIView):
    """GET /api/wallet/history/ – list current user's transactions."""
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class DepositView(APIView):
    """POST /api/wallet/deposit/ – initialise a Paystack payment and return checkout URL."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = DepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount_ngn = serializer.validated_data["amount"]
        email = serializer.validated_data.get("email") or request.user.email
        reference = f"RL-DEP-{uuid.uuid4().hex[:12].upper()}"

        # Create pending transaction locally
        txn = Transaction.objects.create(
            user=request.user,
            transaction_type=Transaction.DEPOSIT,
            amount=amount_ngn,
            reference=reference,
            status=Transaction.PENDING,
        )

        # Call Paystack initialize
        payload = {
            "email": email,
            "amount": int(amount_ngn * 100),   # Paystack uses kobo
            "reference": reference,
            "callback_url": request.build_absolute_uri("/api/wallet/paystack-webhook/"),
            "metadata": {"user_id": request.user.id, "transaction_id": txn.id},
        }
        try:
            resp = requests.post(
                f"{settings.PAYSTACK_BASE_URL}/transaction/initialize",
                headers=_paystack_headers(),
                json=payload,
                timeout=15,
            )
            data = resp.json()
        except requests.RequestException as exc:
            txn.status = Transaction.FAILED
            txn.save(update_fields=["status"])
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        if not data.get("status"):
            txn.status = Transaction.FAILED
            txn.save(update_fields=["status"])
            return Response({"detail": data.get("message", "Paystack error.")}, status=status.HTTP_400_BAD_REQUEST)

        txn.meta = data["data"]
        txn.save(update_fields=["meta"])

        return Response(
            {
                "reference": reference,
                "payment_url": data["data"]["authorization_url"],
                "transaction_id": txn.id,
            },
            status=status.HTTP_201_CREATED,
        )


class WithdrawView(APIView):
    """POST /api/wallet/withdraw/ – request a bank transfer payout."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = WithdrawSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        reference = f"RL-WTH-{uuid.uuid4().hex[:12].upper()}"

        # NOTE: Full Paystack Transfer API requires verified recipients.
        # This creates a pending withdrawal record for processing.
        txn = Transaction.objects.create(
            user=request.user,
            transaction_type=Transaction.WITHDRAW,
            amount=data["amount"],
            reference=reference,
            status=Transaction.PENDING,
            meta={
                "bank_code": data["bank_code"],
                "account_number": data["account_number"],
                "account_name": data["account_name"],
            },
        )
        return Response(
            {"detail": "Withdrawal request submitted.", "reference": reference, "transaction_id": txn.id},
            status=status.HTTP_201_CREATED,
        )


class PaystackWebhookView(APIView):
    """POST /api/wallet/paystack-webhook/ – Paystack event callback."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Verify Paystack signature
        signature = request.headers.get("X-Paystack-Signature", "")
        secret = settings.PAYSTACK_SECRET_KEY.encode()
        body = request.body
        computed = hmac.new(secret, body, hashlib.sha512).hexdigest()

        if computed != signature:
            return Response({"detail": "Invalid signature."}, status=status.HTTP_400_BAD_REQUEST)

        payload = json.loads(body)
        event = payload.get("event")
        data = payload.get("data", {})

        if event == "charge.success":
            reference = data.get("reference", "")
            try:
                from django.db import transaction
                from django.db.models import F
                from .models import Wallet
                
                with transaction.atomic():
                    txn = Transaction.objects.select_for_update().get(reference=reference)
                    if txn.status != Transaction.SUCCESS:
                        txn.status = Transaction.SUCCESS
                        txn.meta = {**txn.meta, "paystack_response": data}
                        txn.save(update_fields=["status", "meta"])
                        
                        if txn.transaction_type == Transaction.DEPOSIT:
                            wallet, _ = Wallet.objects.get_or_create(user=txn.user)
                            wallet.balance = F('balance') + txn.amount
                            wallet.save(update_fields=['balance'])
            except Transaction.DoesNotExist:
                pass

        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class MockDepositView(APIView):
    """POST /api/wallet/mock-deposit/ – bypass Paystack to add funds directly (TESTING ONLY)."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from .models import Wallet
        amount = request.data.get("amount")
        if not amount:
            return Response({"detail": "Amount is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            amount = float(amount)
        except ValueError:
            return Response({"detail": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        wallet.balance += decimal.Decimal(amount)
        wallet.save()

        Transaction.objects.create(
            user=request.user,
            transaction_type=Transaction.DEPOSIT,
            amount=amount,
            reference=f"MOCK-{uuid.uuid4().hex[:10].upper()}",
            status=Transaction.SUCCESS,
            meta={"note": "Mock deposit for testing"}
        )

        return Response({"detail": f"₦{amount} added to your wallet.", "balance": str(wallet.balance)})
