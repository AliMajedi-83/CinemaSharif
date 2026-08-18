from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.db.models import F, Q
from django.core.exceptions import ValidationError 
from datetime import timedelta

class Cinema(models.Model):                                                   # تعریف موجودیت فیزیکی سینما
    name = models.CharField(max_length=120)
    address = models.CharField(max_length=255, blank=True, default="")
    capacity = models.PositiveIntegerField(default=100, verbose_name="ظرفیت سالن") # محدودیت کل منابع در دسترس
    
    def __str__(self) -> str:
        return self.name

class Movie(models.Model):                                                    # تعریف کاتالوگ فیلم‌ها
    title = models.CharField(max_length=200)
    duration_minutes = models.PositiveIntegerField(default=90)
    cast = models.CharField(max_length=255, blank=True, default="", verbose_name="بازیگران")
    summary = models.TextField(blank=True, default="", verbose_name="خلاصه داستان")
    genre = models.CharField(max_length=100, blank=True, default="", verbose_name="ژانر")
    director = models.CharField(max_length=100, blank=True, default="", verbose_name="کارگردان")
    release_year = models.CharField(max_length=4, blank=True, default="", verbose_name="سال ساخت")
    poster = models.ImageField(upload_to='movies/posters/', blank=True, null=True, verbose_name="پوستر فیلم")

    def get_first_cinema_id(self):                                            # متد کمکی برای پیدا کردن اولین سینمای اکران‌کننده
        first_show = self.showtimes.filter(start_at__gte=timezone.now()).first()
        return first_show.cinema_id if first_show else None


    def __str__(self) -> str:
        return self.title

class ShowTime(models.Model):                                                 # مهم‌ترین کلاس: نقطه تلاقی زمان، مکان و کالا
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE, related_name="showtimes")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="showtimes")
    start_at = models.DateTimeField(default=timezone.now)
    capacity = models.PositiveIntegerField(default=50)
    reserved_count = models.PositiveIntegerField(default=0)
    reserved_seats = models.TextField(default="", blank=True)
    base_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    blocked_seats = models.TextField(default="", blank=True, verbose_name="صندلی‌های مسدود شده")
    def __str__(self) -> str:
        return f"{self.movie} @ {self.cinema} - {self.start_at:%Y-%m-%d %H:%M}"

    def get_reserved_seats_list(self):
        return self.reserved_seats.split(',') if self.reserved_seats else []

    @property
    def remaining(self) -> int:                                               # محاسبه داینامیک ظرفیت باقیمانده
        blocked_count = len(self.blocked_seats.split(',')) if self.blocked_seats else 0
        # (: ظرفیت واقعی فروش برابر است با ظرفیت کل منهای رزرو شده‌ها و مسدود شده‌ها)
        return max(0, self.capacity - self.reserved_count - blocked_count)
    @property
    def end_at(self):                                                         # محاسبه زمان پایان سانس بر اساس مدت زمان فیلم
        return self.start_at + timedelta(minutes=self.movie.duration_minutes)
    def clean(self):                                                          # پیاده‌سازی لاجیک پیشگیری از تداخل (Scheduling Logic)
        # (ایده: چک کردن اینکه زمان شروع حتماً در آینده باشد)
        if self.start_at < timezone.now():
            raise ValidationError("زمان شروع سانس نمی‌تواند در گذشته باشد.")

        # پیدا کردن سانس‌هایی که در همان سینما هستند
        overlapping_sessions = ShowTime.objects.filter(
            cinema=self.cinema,
            start_at__lt=self.end_at # سانس‌هایی که قبل از پایان این سانس شروع می‌شن
        ).exclude(pk=self.pk)
        
        for session in overlapping_sessions:
            # (غلط: در صورت یکسان بودن منطقه زمانی (Aware)، این مقایسه بدون خطا انجام می‌شود)
            if self.start_at < session.end_at:                                # الگوریتم تشخیص تداخل زمانی در یک مکان مشترک
                raise ValidationError("تداخل زمانی!")

                

    def save(self, *args, **kwargs):
        self.full_clean() # اجرای متد clean قبل از ذخیره در دیتابیس              # اجبار به اعتبارسنجی قبل از ثبت نهایی داده
        super().save(*args, **kwargs)
    
    class Meta:
        constraints = [                                                       # اعمال محدودیت‌ (Data Integrity)
            models.CheckConstraint(check=Q(capacity__gte=0), name="showtime_capacity_non_negative"),
            models.CheckConstraint(check=Q(reserved_count__gte=0), name="showtime_reserved_non_negative"),
            models.CheckConstraint(check=Q(reserved_count__lte=F("capacity")), name="showtime_reserved_lte_capacity"),
            models.CheckConstraint(check=Q(base_price__gte=0), name="showtime_base_price_non_negative"),
            models.UniqueConstraint(fields=['cinema', 'movie', 'start_at'], name='unique_movie_screening_per_cinema')
        ]

class Reservation(models.Model):                                              # ثبت تراکنش‌های رزرو
    class Status(models.TextChoices):
        CREATED = "CREATED", "Created"
        PAID = "PAID", "Paid"
        CANCELLED = "CANCELLED", "Cancelled"

    class SeatType(models.TextChoices):
        NORMAL = "NORMAL", "Normal"
        VIP = "VIP", "VIP"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservations")
    showtime = models.ForeignKey(ShowTime, on_delete=models.CASCADE, related_name="reservations")
    seat_numbers = models.CharField(max_length=255, default="", blank=True)   # ذخیره شماره صندلی‌ها به صورت رشته متنی
    seat_type = models.CharField(max_length=10, choices=SeatType.choices, default=SeatType.NORMAL)
    seats = models.PositiveIntegerField(default=1)                            # تعداد صندلی‌های رزرو شده در یک فاکتور
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.CREATED)
    created_at = models.DateTimeField(default=timezone.now)
    tracking_code = models.CharField(max_length=64, unique=True, blank=True, null=True) # کد پیگیری یکتا برای کاربر

    def __str__(self) -> str:
        return f"Reservation<{self.id}> {self.user.username}"