"""
Django settings for cinema_project project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()                                                         # بارگذاری متغیرهای حساس از فایل .env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-*5ock@fd91hq_j_jgtnfvi3+n^67$1f9^7ebo2jrk8u)6t02r%')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'                          # کنترل وضعیت خطایابی

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',                                        # برای سه‌رقم سه‌رقم جدا کردن قیمت‌ها در خروجی
    
    # Local apps
    'core',                                                           # اپلیکیشن اصلی (مدیریت فیلم و سانس)
    'accounts',                                                       # مدیریت کاربران و احراز هویت
    'finance',                                                        # مدیریت کیف پول و تراکنش‌های مالی
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cinema_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],                   # آدرس‌دهی پوشه اصلی قالب‌ها برای کل پروژه
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cinema_project.wsgi.application'



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',                    # استفاده از دیتابیس صنعتی PostgreSQL
        'NAME': 'cinema_db',       # اگر فایل env را نخواند، مستقیم اینجا بنویسیم که کار راه بیفتد
        'USER': 'postgres',
        'PASSWORD': '123456',    # رمز عبوری که ست کردی
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Custom User Model (CRITICAL)
AUTH_USER_MODEL = 'accounts.User'                                     # معرفی مدل کاربر اختصاصی)



AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',             #بررسی شباهت
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',                       #حداقل طول رمز
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',                      #پسوردهای رایج
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',                     #فقط عدد نباشد
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'fa-ir'                                               # بومی‌سازی زبان پروژه (فارسی)

TIME_ZONE = 'Asia/Tehran'                                             # تنظیم منطقه زمانی ایران برای سانس‌ها

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',                                              # محل قرارگیری فایل‌های CSS و JS تیم فرانت
]
STATIC_ROOT = BASE_DIR / 'staticfiles'


# Media files (User uploaded files)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'                                       # محل ذخیره پوسترهای فیلم و تصاویر آپلود شده


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Authentication URLs
LOGIN_URL = '/accounts/login/'                                        # مسیر هدایت کاربران غیرمجاز
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'



# Session settings
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = False


# Security settings
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'


# Message framework
from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
}


# Custom settings for cinema project
CINEMA_RESERVATION_TIMEOUT = 600  # 10 minutes in seconds               #  زمان انقضای بلیط اگر شخص پرداخت نکرد
MAX_SEATS_PER_RESERVATION = 10                                        # سقف مجاز خرید بلیط در هر سفارش
