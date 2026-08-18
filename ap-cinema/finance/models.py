# AP-Cinema/finance/models.py
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet",
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    # برای اینکه migration گیر نده روی دیتابیسِ قبلاً ساخته‌شده:
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(balance__gte=0),  # (تغییر: از condition به check)
                name="wallet_balance_non_negative",
            )
        ]

    def __str__(self) -> str:
        return f"Wallet(user={self.user_id}, balance={self.balance})"


class WalletTransaction(models.Model):
    class TxType(models.TextChoices):
        DEBIT = "DEBIT", "Debit"
        CREDIT = "CREDIT", "Credit"

    class Status(models.TextChoices):
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=10, choices=TxType.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SUCCESS)
    description = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        indexes = [
            models.Index(fields=["wallet", "created_at"]),
            models.Index(fields=["type", "status"]),
        ]

    def __str__(self) -> str:
        return (
            f"WalletTransaction(wallet={self.wallet_id}, "
            f"type={self.type}, amount={self.amount}, status={self.status})"
        )
