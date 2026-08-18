# core/patterns/singleton.py

class SystemConfig:
    _instance = None                                                          # متغیر استاتیک برای ذخیره تنها نمونه موجود در حافظه
    
    def __new__(cls):                                                         # متدی که قبل از __init__ اجرا می‌شود تا ساخت شیء را کنترل کند
        if cls._instance is None:                                             # چک کردن اینکه آیا قبلاً نمونه‌ای ساخته شده یا خیر
            cls._instance = super(SystemConfig, cls).__new__(cls)             # ساخت اولین و آخرین نمونه از کلاس
            # مقادیر پیش‌فرض تنظیمات سیستم
            cls._instance.min_ticket_price = 50000                            # حداقل قیمت بلیط (کف قیمت)
            cls._instance.max_seats_per_booking = 10                          # سقف مجاز خرید در هر تراکنش
            cls._instance.reservation_timeout = 15 * 60  # 15 minutes         # زمان انقضای رزرو موقت
        return cls._instance                                                  # بازگرداندن همان نمونه قبلی (جلوگیری از ساخت شیء جدید)

    def get_config(self, key):                                                # متد عمومی برای خواندن تنظیمات
        return getattr(self, key, None)

    def set_config(self, key, value):                                         # متد عمومی برای تغییر آنی تنظیمات در کل سیستم
        setattr(self, key, value)