from django.contrib import admin
from core.models import Cinema, Movie, ShowTime, Reservation

@admin.register(Cinema)                                                       # ثبت مدل سینما در پنل ادمین
class CinemaAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "address")                                  # فیلدهایی که در جدول کلی نمایش داده می‌شوند
    search_fields = ("name",)                                                 # قابلیت جستجو بر اساس نام سینما

@admin.register(Movie)                                                        # ثبت مدل فیلم
class MovieAdmin(admin.ModelAdmin):
    # این خطوط تغییر کردند تا فیلدهای جدید نمایش داده شوند
    list_display = ("id", "title", "genre", "director", "duration_minutes")   # نمایش مشخصات فنی فیلم برای ادمین
    search_fields = ("title", "director", "genre")                            # جستجوی چندگانه برای پیدا کردن سریع فیلم

@admin.register(ShowTime)                                                     # ثبت مدل سانس (مدیریت زمان‌بندی)
class ShowTimeAdmin(admin.ModelAdmin):
    list_display = ("id", "movie", "cinema", "start_at", "capacity", "reserved_count", "base_price") # نمایش وضعیت ظرفیت در یک نگاه
    list_filter = ("cinema", "movie")                                         # فیلتر هوشمند برای جداسازی سانس‌های یک سینمای خاص
    search_fields = ("movie__title", "cinema__name")                          # جستجو در جداول مرتبط با استفاده از دو زیرخط (Double Underscore)

@admin.register(Reservation)                                                  # ثبت مدل رزرو (مدیریت فروش)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "showtime", "seats", "seat_type", "total_price", "status", "created_at")
    list_filter = ("status", "seat_type")                                     # فیلتر بر اساس وضعیت پرداخت و نوع صندلی (VIP/Normal)
    search_fields = ("user__username",)                                       # پیگیری رزروها بر اساس نام کاربری مشتری