from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout, authenticate, login
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.db import IntegrityError
from .models import User

# --- فرم اختصاصی لاگین با شماره تماس ---
class PhoneAuthForm(AuthenticationForm):                                      # سفارشی‌سازی فرم پیش‌فرض برای پشتیبانی از شماره موبایل
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            try:
                user_obj = User.objects.get(phone_number=username)            # جستجوی کاربر بر اساس شماره موبایل به جای نام کاربری
                actual_username = user_obj.username                           # استخراج نام کاربری واقعی برای سیستم احراز هویت جنگو
            except User.DoesNotExist:
                actual_username = username

            self.user_cache = authenticate(self.request, username=actual_username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()                          # مدیریت خطای ورود در صورت اشتباه بودن رمز یا یوزر
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data

class UserLoginView(LoginView):
    template_name = 'accounts/login.html'                                     # مسیردهی به قالب گرافیکی صفحه ورود
    form_class = PhoneAuthForm
    
def custom_logout(request):
    logout(request)                                                           # خروج امن کاربر و ابطال نشست (Session)
    return redirect('core:home')

def check_phone(request):                                                     # متد کمکی برای UX: بررسی وجود شماره قبل از ورود کامل
    phone = request.GET.get('phone', '')
    exists = User.objects.filter(phone_number=phone).exists()                 # بررسی در دیتابیس برای پاسخ به درخواست‌های AJAX
    return JsonResponse({'exists': exists})

# --- تابع جدید برای ثبت‌نام (این ارور شما را حل می‌کند) ---
def register_view(request):
    if request.method == 'POST':                                              # پردازش اطلاعات ارسالی از فرم ثبت‌نام
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        
        try:
            # ساختن یوزر جدید در دیتابیس
            user = User.objects.create_user(                                  # استفاده از متد امن جنگو برای هش کردن پسورد
                username=username,
                password=password,
                phone_number=phone,
                first_name=full_name
            )
            # لاگین خودکار کاربر بلافاصله پس از ثبت‌نام
            login(request, user)                                              # ورود خودکار برای بهبود تجربه کاربری (User Experience)
            return redirect('core:home')
        except IntegrityError:                                                # مدیریت خطای هم‌پوشانی داده‌ها (مثل یوزرنیم تکراری)
            # خطای تکراری بودن یوزرنیم یا شماره موبایل
            return render(request, 'accounts/register.html', {
                'error': 'این نام کاربری یا شماره موبایل قبلاً ثبت شده است!'
            })
            
    return render(request, 'accounts/register.html')