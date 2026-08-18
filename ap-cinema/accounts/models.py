"""
Custom User model for AP-Cinema project.
Extends Django's AbstractUser with phone_number and role fields.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """
    مدل کاربر سفارشی برای سیستم سینما
    شامل فیلدهای اضافی برای شماره تماس و نقش کاربر
    """
    
    # نقش‌های کاربر
    ROLE_CHOICES = [                                                      # تعریف نقش‌های سیستم برای تفکیک دسترسی‌ها
        ('customer', 'مشتری'),
        ('admin', 'مدیر'),
    ]
    
    # Validator برای شماره تماس ایرانی
    phone_regex = RegexValidator(                                         # تضمین ورود صحیح شماره موبایل با الگوی 09
        regex=r'^09\d{9}$',
        message="شماره تماس باید به صورت 09xxxxxxxxx باشد (11 رقم)"
    )
    
    # فیلدهای اضافی
    phone_number = models.CharField(                                      # فیلد کلیدی برای لاگین (Unique بودن حیاتی است)
        max_length=11,
        unique=True,
        validators=[phone_regex],
        verbose_name='شماره تماس',
        help_text='شماره موبایل 11 رقمی به صورت 09xxxxxxxxx'
    )
    
    role = models.CharField(                                              # اختصاص نقش به کاربر در زمان ثبت‌نام
        max_length=10,
        choices=ROLE_CHOICES,
        default='customer',
        verbose_name='نقش کاربر'
    )
    
    # فیلدهای تاریخ
    created_at = models.DateTimeField(                                    # ثبت خودکار زمان ایجاد اکانت
        auto_now_add=True,
        verbose_name='تاریخ ثبت‌نام'
    )
    
    updated_at = models.DateTimeField(                                    # به‌روزرسانی خودکار در هر تغییر مشخصات
        auto_now=True,
        verbose_name='تاریخ به‌روزرسانی'
    )
    
    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        ordering = ['-created_at']                                        # نمایش لیست کاربران از جدیدترین به قدیمی‌ترین
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.phone_number})"            # فرمت نمایش کاربر در لیست‌ها و پنل ادمین
    
    def get_full_name(self):
        """
        بازگرداندن نام کامل کاربر
        """
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username
    
    def is_admin(self):
        """
        بررسی اینکه آیا کاربر ادمین است یا خیر
        """
        return self.role == 'admin' or self.is_staff or self.is_superuser 
    
    def is_customer(self):
        """
        بررسی اینکه آیا کاربر مشتری است یا خیر
        """
        return self.role == 'customer'