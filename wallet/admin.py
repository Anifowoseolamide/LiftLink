from django.contrib import admin
from .models import Transaction, Wallet, EscrowRecord


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance")
    search_fields = ("user__username", "user__email")


@admin.register(EscrowRecord)
class EscrowRecordAdmin(admin.ModelAdmin):
    list_display = ("booking", "amount", "status")
    list_filter = ("status",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "transaction_type", "amount", "reference", "status", "created_at")
    list_filter = ("transaction_type", "status")
    search_fields = ("user__username", "reference")
    readonly_fields = ("reference", "meta", "created_at")
