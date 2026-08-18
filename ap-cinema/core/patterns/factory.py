# core/patterns/factory.py
import random
import string
from dataclasses import dataclass
from django.utils import timezone
from decimal import Decimal

# --- بخش بدون تغییر: ساختار درخواست رزرو ---
@dataclass
class ReservationRequest:
    user_id: int
    showtime_id: int
    seats: int
    reservation_type: str  # 'normal' or 'vip'

# +++ بخش جدید: تعریف استراتژی‌های محاسبه قیمت (Strategy Pattern) +++
class PriceStrategy:
    def calc_price(self, base_price: int, seats: int) -> int:
        raise NotImplementedError

class NormalPriceStrategy(PriceStrategy):
    def calc_price(self, base_price: int, seats: int) -> int:
        return base_price * seats

class VIPPriceStrategy(PriceStrategy):
    def calc_price(self, base_price: int, seats: int) -> int:
        # صندلی VIP طبق منطق سیستم ۵۰ درصد گران‌تر است
        return int(base_price * seats * 1.5)

# --- کلاس اصلی کارخانه ---
class ReservationFactory:
    
    # +++ متد حیاتی که در services.py صدا زده شده و وجود نداشت (تغییر) +++
    @staticmethod
    def get_strategy(res_type: str) -> PriceStrategy:
        """انتخاب استراتژی محاسبه قیمت بر اساس نوع صندلی"""
        strategies = {
            'normal': NormalPriceStrategy(),
            'vip': VIPPriceStrategy(),
        }
        return strategies.get(res_type.lower(), NormalPriceStrategy())

    @staticmethod
    def _generate_tracking_code(length: int = 10) -> str:
        alphabet = string.ascii_uppercase + string.digits
        return "".join(random.choice(alphabet) for _ in range(length))

    @staticmethod
    def create_reservation(user, showtime, seats: int, seat_type: str, total_price):
        from core.models import Reservation  # late import برای جلوگیری از circular import

        tracking = ReservationFactory._generate_tracking_code()

        # +++ اصلاح نام فیلد: تغییر screening به showtime برای تطبیق با مدل (تغییر) +++
        return Reservation.objects.create(
            user=user,
            showtime=showtime,
            seats=seats,
            seat_type=seat_type,
            total_price=total_price,
            status=Reservation.Status.PAID,
            tracking_code=tracking,
            created_at=timezone.now(),
        )

        