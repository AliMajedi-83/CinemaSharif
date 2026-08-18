from django.contrib import admin
from finance.models import Wallet, WalletTransaction

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "balance", "updated_at")
    search_fields = ("user__username",)

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "wallet", "type", "amount", "status", "created_at")
    list_filter = ("type", "status")
