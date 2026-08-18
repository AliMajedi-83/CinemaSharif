from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.core.exceptions import ObjectDoesNotExist

from core.models import Reservation, ShowTime
from core.services import reserve_seats, ReservationError, cancel_reservation


@require_POST                                                                 # محدود کردن متد به POST برای امنیت داده‌ها
@login_required                                                               # اطمینان از اینکه فقط کاربر لاگین شده تست انجام دهد
def reserve_test(request):                                                    # تست سریع رزرو از طریق درخواست‌های POST
    showtime_id = int(request.POST.get("showtime_id"))
    seats = int(request.POST.get("seats", 1))
    seat_type = request.POST.get("seat_type", Reservation.SeatType.NORMAL)

    try:
        r = reserve_seats(user=request.user, showtime_id=showtime_id, seats=seats, seat_type=seat_type)
        return JsonResponse({"ok": True, "reservation_id": r.id, "total_price": str(r.total_price)})
    except ReservationError as e:                                             # مدیریت خطاهای بیزنس‌لاجیک رزرو (مثلاً نبود ظرفیت)
        return JsonResponse({"ok": False, "error": str(e)}, status=400)


@require_GET                                                                  # امکان تست سریع رزرو فقط با وارد کردن یک URL در مرورگر
def reserve_test_get(request):
    # 1) ورودی‌ها بدون crash
    try:
        showtime_id = get_int_param(request, "showtime_id", min_value=1)
        seats = get_int_param(request, "seats", default=1, min_value=1)
    except ValueError as e:                                                   # جلوگیری از کرش کردن سرور با ورودی‌های نامعتبر
        return json_error(str(e), 400)

    seat_type = request.GET.get("seat_type", "NORMAL").upper()
    if seat_type not in ("NORMAL", "VIP"):
        return json_error("invalid seat_type (use NORMAL or VIP)", 400)

    # 2) اگر showtime وجود نداشت، JSON بده نه صفحه زرد
    try:
        ShowTime.objects.get(id=showtime_id)
    except ShowTime.DoesNotExist:                                             # مدیریت خطای عدم وجود رکورد (404 دستی)
        return json_error("showtime not found", 404)

    # 3) حالا منطق رزروت رو صدا بزن (همون که قبلاً داشتی)
    # فرض: سرویس reserve_seats داری
    from core.services import reserve_seats                                   # (ایده: ایمپورت محلی برای جلوگیری از Circular Import احتمالی)

    try:
        r = reserve_seats(
            user=request.user,
            showtime_id=showtime_id,
            seats=seats,
            seat_type=seat_type,
        )
        # r باید دیکشنری مثل {"ok": True, ...} بده
        return JsonResponse(r, status=200 if r.get("ok") else 400)
    except Exception as e:
        # برای dev endpoint بد نیست (ولی بهتره لاگ هم بزنی)
        return json_error(f"unexpected error: {e}", 500)

@require_GET
def cancel_test_get(request):                                                 # تست سریع ابطال رزرو برای پاکسازی دیتابیس در زمان تست
    try:
        reservation_id = get_int_param(request, "reservation_id", min_value=1)
    except ValueError as e:
        return json_error(str(e), 400)

    from core.services import cancel_reservation

    try:
        r = cancel_reservation(user=request.user, reservation_id=reservation_id)
        return JsonResponse(r, status=200 if r.get("ok") else 400)
    except Reservation.DoesNotExist:
        return json_error("reservation not found", 404)
    except Exception as e:
        return json_error(f"unexpected error: {e}", 500)

def json_error(msg: str, status: int = 400):                                  # تابع کمکی برای یکپارچه‌سازی پاسخ‌های خطای JSON
    return JsonResponse({"ok": False, "error": msg}, status=status)

def get_int_param(request, key: str, default=None, *, min_value=None):        # پارسر هوشمند اعداد برای جلوگیری از خطاهای نوع داده
    """
    Safe int parser:
    - اگر نبود و default داری => default
    - اگر نبود و default نداری => ValueError
    - اگر عدد نبود => ValueError
    - اگر min_value داشته باشه و کمتر بود => ValueError
    """
    raw = request.GET.get(key, None)
    if raw is None:
        if default is not None:
            return default
        raise ValueError(f"missing {key}")

    try:
        val = int(raw)
    except (TypeError, ValueError):
        raise ValueError(f"invalid {key}")

    if min_value is not None and val < min_value:
        raise ValueError(f"{key} must be >= {min_value}")

    return val