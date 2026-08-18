"""
Core Business Logic for Reservations - AP-Cinema Project
Week 4 Implementation - Tafti (Logic Layer)
"""
from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.utils import timezone

from core.db.transactions import get_object_for_update
from core.models import ShowTime, Reservation
from finance.utils import (
    ensure_wallet_exists,
    get_wallet_for_update,
    debit_wallet,
    credit_wallet,   # ✅ لازم برای cancel
)
from finance.models import WalletTransaction  # ✅ برای REFUND type


# ============================================================================
# Custom Exception for Reservation Errors
# ============================================================================

class ReservationError(Exception):
    """Raised when a reservation cannot be completed."""
    pass


# ============================================================================
# Helper Functions (Private)
# ============================================================================

def _to_money(value: Decimal) -> Decimal:
    """Round decimal to 2 decimal places for currency."""
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _normalize_seat_type(seat_type: str) -> str:
    """
    Normalize seat_type: accepts 'vip', 'VIP', 'normal', ...
    Returns value compatible with Reservation.SeatType.*
    """
    if seat_type is None:
        raise ReservationError("نوع صندلی ارسال نشده است")

    st = str(seat_type).strip().upper()

    allowed = {Reservation.SeatType.NORMAL, Reservation.SeatType.VIP}

    if st in allowed:
        return st

    if st == "NORMAL":
        return Reservation.SeatType.NORMAL
    if st == "VIP":
        return Reservation.SeatType.VIP

    raise ReservationError(f"نوع صندلی نامعتبر است: {seat_type}")


def _calculate_total_price(*, showtime: ShowTime, seats: int, seat_type: str, user) -> Decimal:
    """
    Calculate total price.
    Tries Factory pattern; falls back to simple calculation.
    """
    base = _to_money(showtime.base_price)

    try:
        from core.patterns.factory import ReservationRequest, ReservationFactory

        request = ReservationRequest(
            user_id=getattr(user, "id", None),
            showtime_id=showtime.id,
            seats=seats,
            reservation_type=str(seat_type).lower(),
        )
        strategy = ReservationFactory.get_strategy(request.reservation_type)

        total = strategy.calc_price(int(base), seats)
        return _to_money(Decimal(total))
    except Exception:
        multiplier = Decimal("1.5") if seat_type == Reservation.SeatType.VIP else Decimal("1.0")
        return _to_money(base * Decimal(seats) * multiplier)


def _generate_tracking_code() -> str:
    """
    Generate unique tracking code.
    Safer uniqueness: CINEMA-YYYYMMDDHHMMSS-<micro>-<rand4>
    """
    import random
    import string

    now = timezone.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    micro = f"{now.microsecond:06d}"
    rand4 = "".join(random.choices(string.digits, k=4))
    return f"CINEMA-{timestamp}-{micro}-{rand4}"


# ============================================================================
# Main Reservation Logic (Public API)
# ============================================================================

@transaction.atomic
def reserve_seats(*, user, showtime_id: int, seats: list, seat_type: str) -> Reservation: # (تغییر: seats اکنون یک لیست است)
    """
    ثبت رزرو با پشتیبانی از انتخاب چندین صندلی 
    """

    # === STEP 1: Validate Inputs ===
    # (غلط: در نسخه قبلی seats = int(seats) بود که روی لیست خطا می‌داد)
    if not seats or not isinstance(seats, list):
        raise ReservationError("لیست صندلی‌ها نامعتبر است")

    num_seats = len(seats) # (ایده: محاسبه خودکار تعداد صندلی از روی طول لیست)
    seat_numbers_str = ",".join(map(str, seats)) # تبدیل لیست به رشته برای ذخیره

    if num_seats > 10:  
        raise ReservationError("حداکثر 10 صندلی در هر رزرو مجاز است") 

    seat_type = _normalize_seat_type(seat_type)

    # === STEP 2 & 3: Lock & Capacity Check ===
    showtime = get_object_for_update(ShowTime.objects, id=showtime_id)
    
    if showtime.remaining < num_seats: # (تغییر: مقایسه با تعداد صندلی‌های انتخاب شده)
        raise ReservationError(f"ظرفیت کافی نیست. تنها {showtime.remaining} صندلی باقی‌مانده است")

    # === STEP 4: Calculate Total Price ===
    total_price = _calculate_total_price(
        showtime=showtime,
        seats=num_seats, # ارسال تعداد به استراتژی قیمت‌گذاری
        seat_type=seat_type,
        user=user,
    )

    # === STEP 5: Lock Wallet (CRITICAL for concurrency) ===
    ensure_wallet_exists(user)
    wallet = get_wallet_for_update(user)

    # === STEP 6: Debit Wallet ===
    try:
        debit_wallet(
            wallet=wallet,
            amount=total_price,
            description=f"رزرو سانس {getattr(showtime.movie, 'title', showtime.id)} در {getattr(showtime.cinema, 'name', '')}",
        )
    except (ValueError, Exception) as e:
        raise ReservationError(f"موجودی کیف پول کافی نیست: {str(e)}")
# (ایده: استفاده از Factory برای رعایت الگوی طراحی پروژه) [cite: 193]
    from core.patterns.factory import ReservationFactory
    reservation = ReservationFactory.create_reservation(
        user=user,
        showtime=showtime,
        seats=num_seats,
        seat_type=seat_type,
        total_price=total_price
    )
    reservation.seat_numbers = seat_numbers_str
    reservation.save()

    # === STEP 8: Update ShowTime Capacity ===
    showtime.reserved_count += num_seats
    
    # اضافه کردن صندلی‌های جدید به لیست رزرو شده‌های سانس 
    current_reserved = showtime.reserved_seats.split(',') if showtime.reserved_seats else []
    current_reserved.extend(map(str, seats))
    showtime.reserved_seats = ",".join(filter(None, current_reserved))
    
    showtime.save(update_fields=["reserved_count", "reserved_seats"])

    return reservation


@transaction.atomic
def cancel_reservation(*, user, reservation_id: int) -> Reservation:
    """
    Cancel a reservation and refund to wallet (idempotent).
    """
    try:
        reservation = Reservation.objects.select_for_update().select_related("showtime").get(id=reservation_id)
    except Reservation.DoesNotExist:
        raise ReservationError("رزرو یافت نشد")

    if reservation.user_id != user.id:
        raise ReservationError("شما مجاز به لغو این رزرو نیستید")

    # idempotent
    if reservation.status == Reservation.Status.CANCELLED:
        return reservation

    if reservation.status != Reservation.Status.PAID:
        raise ReservationError("فقط رزروهای پرداخت‌شده قابل لغو هستند")

    # Lock ShowTime
    showtime = ShowTime.objects.select_for_update().get(id=reservation.showtime_id)

    # Lock Wallet and refund
    ensure_wallet_exists(user)
    wallet = get_wallet_for_update(user)

    try:
        credit_wallet(
            wallet=wallet,
            amount=reservation.total_price,
            description=f"بازگشت وجه رزرو {reservation.tracking_code}",
            tx_type=getattr(WalletTransaction.Type, "REFUND", None),
        )
    except TypeError:
        credit_wallet(
            wallet=wallet,
            amount=reservation.total_price,
            description=f"بازگشت وجه رزرو {reservation.tracking_code}",
        )

    # Restore capacity
    if showtime.reserved_count < reservation.seats:
        raise ReservationError("خطای داخلی: تعداد رزرو نامعتبر است")

    showtime.reserved_count -= reservation.seats

    # +++ بخش جدید: آزاد کردن صندلی‌ها روی نقشه هنگام لغو بلیت +++
    if reservation.seat_numbers and showtime.reserved_seats:
        canceled_seats = set(reservation.seat_numbers.split(','))
        current_seats = set(showtime.reserved_seats.split(','))
        updated_seats = current_seats - canceled_seats
        # تبدیل دوباره به رشته با حذف فاصله‌های خالی احتمالی
        showtime.reserved_seats = ",".join(filter(None, updated_seats))

    showtime.save(update_fields=["reserved_count", "reserved_seats"])

    # Update reservation status
    reservation.status = Reservation.Status.CANCELLED
    if hasattr(reservation, "cancelled_at"):
        reservation.cancelled_at = timezone.now()
        reservation.save(update_fields=["status", "cancelled_at"])
    else:
        reservation.save(update_fields=["status"])

    return reservation