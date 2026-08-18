from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.utils import timezone
from core.models import Movie, Reservation, Cinema, ShowTime
from accounts.models import User
import random
from django.core.exceptions import ValidationError 
from django.utils.timezone import make_aware
from datetime import datetime
# --- Helper Function ---
def is_admin(user):                                                           # لایه امنیتی برای اطمینان از دسترسی فقط ادمین‌ها
    return user.is_authenticated and (user.is_staff or user.role == 'admin')

# ==========================
# بخش داشبورد (Dashboard)
# ==========================
@user_passes_test(is_admin, login_url='/accounts/login/')
def admin_dashboard(request):                                                 # تحلیل شاخص‌های کلیدی عملکرد (KPIs)
    """نمایش آمار کلی در داشبورد"""
    total_tickets = Reservation.objects.filter(status='PAID').aggregate(Sum('seats'))['seats__sum'] or 0
    active_movies = Movie.objects.count()
    total_revenue = Reservation.objects.filter(status='PAID').aggregate(Sum('total_price'))['total_price__sum'] or 0
    new_users = User.objects.count()
    return render(request, 'admin/dashboard.html', locals())

# ==========================
# بخش مدیریت سینماها (Cinema)
# ==========================
@user_passes_test(is_admin)
def admin_cinema_mgmt(request):
    cinemas = Cinema.objects.all()
    return render(request, 'admin/cinema_mgmt.html', {'cinemas': cinemas})

@user_passes_test(is_admin, login_url='/accounts/login/')
def admin_cinema_upsert(request, cinema_id=None):                             # مدیریت هوشمند تغییرات ظرفیت سالن
    cinema = get_object_or_404(Cinema, id=cinema_id) if cinema_id else None
    
    if request.method == 'POST':
        name = request.POST.get('name')
        try:
            new_capacity = int(request.POST.get('capacity', 0))
        except (ValueError, TypeError):
            messages.error(request, "خطا: ظرفیت باید عدد باشد.")
            return redirect('core:admin_cinema_mgmt')

        if cinema:
            future_showtimes = ShowTime.objects.filter(cinema=cinema, start_at__gt=timezone.now())
            
            for st in future_showtimes:
                # چک کردن اینکه ظرفیت جدید کمتر از بلیت‌های فروخته شده نباشد
                if new_capacity < st.reserved_count:                          # کنترل محدودیت در تغییرات نزولی ظرفیت
                    messages.error(request, f"خطا: در سانس {st.start_at.strftime('%H:%M')} تعداد {st.reserved_count} بلیت فروخته شده. کاهش به این مقدار ممکن نیست.")
                    return redirect('core:admin_cinema_mgmt')

                # +++ منطق جدید: مدیریت صندلی‌ها بدون حذف فیزیکی +++
                
                # سناریو الف: افزایش ظرفیت
                if new_capacity > st.capacity:
                    # (ایده: اگر ظرفیت فیزیکی زیاد شد، صندلی‌های جدید به ته سالن اضافه می‌شوند)
                    st.capacity = new_capacity
                    # در افزایش ظرفیت، تمام مسدودی‌های قبلی را پاک می‌کنیم تا سالن باز شود
                    st.blocked_seats = "" 
                
                # سناریو ب: کاهش ظرفیت (نارنجی کردن رندوم)
                elif new_capacity < st.capacity:                              # پیاده‌سازی الگوریتم مسدودسازی در صورت خرابی صندلی‌ها
                    # هدف: مجموع (رزرو شده + آزاد) نباید از new_capacity بیشتر باشد
                    # پس باید به تعداد (st.capacity - new_capacity) صندلی را مسدود کنیم
                    diff = st.capacity - new_capacity
                    
                    reserved_set = set(st.get_reserved_seats_list())
                    # تمام صندلی‌های فعلی که رزرو نشده‌اند
                    all_free_seats = [str(i) for i in range(1, st.capacity + 1) if str(i) not in reserved_set]
                    
                    # انتخاب رندوم از بین صندلی‌های آزاد برای مسدود کردن
                    if len(all_free_seats) >= diff:
                        blocked_list = random.sample(all_free_seats, diff)    # الگوریتم انتخاب تصادفی برای مسدود کردن صندلی‌ها
                        st.blocked_seats = ",".join(blocked_list)
                    else:
                        # اگر صندلی آزاد کافی نبود (نباید رخ دهد چون بالا چک کردیم)
                        st.blocked_seats = ",".join(all_free_seats)

                # (غلط: در نسخه قبلی st.capacity همیشه برابر new_capacity می‌شد که باعث حذف صندلی از UI می‌گشت)
                st.save(update_fields=['capacity', 'blocked_seats'])          # بهینه‌سازی دیتابیس با بروزرسانی فقط فیلدهای مورد نیاز

            cinema.name = name
            cinema.capacity = new_capacity
            cinema.save()
            messages.success(request, f"ظرفیت تغییر یافت. صندلی‌های مازاد در سانس‌های آینده مسدود شدند.")
        else:
            Cinema.objects.create(name=name, capacity=new_capacity)
            messages.success(request, "سینمای جدید ایجاد شد.")
            
        return redirect('core:admin_cinema_mgmt')
    return render(request, 'admin/cinema_form.html', {'cinema': cinema})

@user_passes_test(is_admin)
def admin_cinema_delete(request, cinema_id):
    if request.method == 'POST':
        get_object_or_404(Cinema, id=cinema_id).delete()
        messages.success(request, 'سینما حذف شد.')
    return redirect('core:admin_cinema_mgmt')

# ==========================
# بخش مدیریت فیلم‌ها (Movie)
# ==========================
@user_passes_test(is_admin)
def admin_movie_mgmt(request):
    movies = Movie.objects.all()
    return render(request, 'admin/movie_mgmt.html', {'movies': movies})

@user_passes_test(is_admin)
def admin_movie_upsert(request, movie_id=None):
    movie = get_object_or_404(Movie, id=movie_id) if movie_id else None
    
    if request.method == 'POST':
        try:
            duration = int(request.POST.get('duration', 0))
        except:
            duration = 0

        data = {
            'title': request.POST.get('title'),
            'genre': request.POST.get('genre'),
            'director': request.POST.get('director'),
            'duration_minutes': duration,
            'summary': request.POST.get('description'), 
            'cast': request.POST.get('cast', ''),
            'release_year': request.POST.get('release_year', ''),
        }
        
        poster = request.FILES.get('poster')                                  # مدیریت فایل‌های چندرسانه‌ای (پوستر فیلم)
        if movie:
            for key, value in data.items():
                setattr(movie, key, value)
            if poster: movie.poster = poster
            movie.save()
            messages.success(request, "فیلم به‌روزرسانی شد.")
        else:
            Movie.objects.create(**data, poster=poster)
            messages.success(request, "فیلم جدید اضافه شد.")
            
        return redirect('core:admin_movie_mgmt')
    return redirect('core:admin_movie_mgmt')

@user_passes_test(is_admin)
def admin_movie_delete(request, movie_id):
    if request.method == "POST":
        get_object_or_404(Movie, id=movie_id).delete()
        messages.success(request, "فیلم حذف شد.")
    return redirect('core:admin_movie_mgmt')

# ==========================
# بخش برنامه اکران (Screening)
# ==========================
@user_passes_test(is_admin)
def admin_screening_mgmt(request):
    """مدیریت برنامه اکران"""
    context = {
        'movies': Movie.objects.all(),
        'cinemas': Cinema.objects.all(),
        'showtimes': ShowTime.objects.all().select_related('movie', 'cinema').order_by('-start_at') # استفاده از select_related برای کاهش کوئری‌ها
    }
    return render(request, 'admin/screening_mgmt.html', context)

@user_passes_test(is_admin)
def admin_screening_create(request):
    if request.method == 'POST':
        cinema_id = request.POST.get('cinema')
        movie_id = request.POST.get('movie')
        start_at = f"{request.POST.get('date')} {request.POST.get('start_time')}"
        
        cinema = get_object_or_404(Cinema, id=cinema_id)
        # (ایده: اختصاص خودکار ظرفیت سالن به سانس جدید در لحظه ایجاد)
        raw_date_str = f"{request.POST.get('date')} {request.POST.get('start_time')}"
        naive_datetime = datetime.strptime(raw_date_str, '%Y-%m-%d %H:%M')
        start_at = make_aware(naive_datetime) # تبدیل به زمان Aware
        

        try:
            ShowTime.objects.create(                                          # ایجاد سانس جدید با رعایت قیدهای دیتابیس
                cinema=cinema,
                movie_id=movie_id,
                start_at=start_at,
                base_price=request.POST.get('price'),
                capacity=cinema.capacity
            )
            messages.success(request, "سانس با موفقیت ثبت شد.")
        except ValidationError as e:                                          # مدیریت خطاهای اعتبارسنجی (مثل تداخل زمانی)
            
            # (ایده: ویژگی e.messages یک لیست از تمام پیام‌های خطا بدون نام فیلدهاست)
            for message in e.messages:
                messages.error(request, message)
        except Exception as e:
            messages.error(request, f"خطای غیرمنتظره: {str(e)}")
            
    return redirect('core:admin_screening_mgmt')

@user_passes_test(is_admin)
def admin_screening_delete(request, screening_id):
    if request.method == 'POST':
        get_object_or_404(ShowTime, id=screening_id).delete()
        messages.success(request, 'سانس حذف شد.')
    return redirect('core:admin_screening_mgmt')