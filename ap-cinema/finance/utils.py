# AP-Cinema/finance/utils.py
from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction

from finance.models import Wallet, WalletTransaction


def _to_money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def ensure_wallet_exists(user) -> Wallet:
    wallet, _ = Wallet.objects.get_or_create(user=user)
    return wallet


def get_wallet_for_update(user) -> Wallet:
    # مهم: داخل transaction.atomic صدا زده شود
    return Wallet.objects.select_for_update().get(user=user)


@transaction.atomic
def credit_wallet(*, wallet: Wallet, amount: Decimal, description: str = "") -> WalletTransaction:
    amount = _to_money(Decimal(amount))
    if amount <= 0:
        raise ValueError("Amount must be positive")

    wallet.balance = _to_money(wallet.balance + amount)
    wallet.save(update_fields=["balance", "updated_at"])

    return WalletTransaction.objects.create(
        wallet=wallet,
        amount=amount,
        type=WalletTransaction.TxType.CREDIT,
        status=WalletTransaction.Status.SUCCESS,
        description=description,
    )


@transaction.atomic
def debit_wallet(*, wallet: Wallet, amount: Decimal, description: str = "") -> WalletTransaction:
    amount = _to_money(Decimal(amount))
    if amount <= 0:
        raise ValueError("Amount must be positive")

    if wallet.balance < amount:
        raise ValueError(f"Insufficient balance. Need {amount}, have {wallet.balance}")

    wallet.balance = _to_money(wallet.balance - amount)
    wallet.save(update_fields=["balance", "updated_at"])

    return WalletTransaction.objects.create(
        wallet=wallet,
        amount=amount,
        type=WalletTransaction.TxType.DEBIT,
        status=WalletTransaction.Status.SUCCESS,
        description=description,
    )
