from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Movie, Cinema, ShowTime, Reservation
from core.services import reserve_seats

# --- بخش ویوهای عمومی ---

def home(request):
    movies = Movie.objects.filter(showtimes__start_at__gte=timezone.now()).distinct()[:8]     # نمایش ۸ فیلم برتر که سانس فعال دارند
    return render(request, 'core/home.html', {'movies': movies})

def cinema_list(request):
    query = request.GET.get('q')
    cinemas = Cinema.objects.filter(name__icontains=query) if query else Cinema.objects.all() # قابلیت جستجوی متنی در نام سینماها
    return render(request, 'core/cinema_list.html', {'cinemas': cinemas})

def movie_list(request, cinema_id=None):
    active_movies = Movie.objects.filter(showtimes__start_at__gte=timezone.now()).distinct()
    
    if cinema_id:
        cinema = get_object_or_404(Cinema, id=cinema_id)
        movies = active_movies.filter(showtimes__cinema=cinema)
    else:
        cinema, movies = None, active_movies

    # اعمال فیلترهای پویا (ژانر، سال، جستجو)
    genre_query = request.GET.get('genre')                                                    # دریافت پارامتر ژانر از URL
    year_query = request.GET.get('year')
    search_query = request.GET.get('q')

    if genre_query: movies = movies.filter(genre__icontains=genre_query)                      # فیلتر داینامیک بر اساس ژانر منتخب
    if year_query: movies = movies.filter(release_year=year_query)
    if search_query: movies = movies.filter(title__icontains=search_query)

    context = {
        'movies': movies, 
        'cinema': cinema,
        'all_genres': active_movies.values_list('genre', flat=True).distinct(),               # استخراج لیست ژانرها برای منوی فیلتر
        'all_years': active_movies.values_list('release_year', flat=True).distinct().order_by('-release_year'),
    }
    return render(request, 'core/movie_list.html', context)

def showtime_detail(request, cinema_id, movie_id):
    cinema = get_object_or_404(Cinema, id=cinema_id)
    movie = get_object_or_404(Movie, id=movie_id)
    showtimes = ShowTime.objects.filter(cinema=cinema, movie=movie, start_at__gte=timezone.now()).order_by('start_at')
    available_cinemas = Cinema.objects.filter(showtimes__movie=movie).distinct()              # نمایش سینماهای دیگری که این فیلم را دارند
    
    return render(request, 'core/showtime_detail.html', {
        'cinema': cinema, 
        'movie': movie, 
        'showtimes': showtimes,
        'available_cinemas': available_cinemas
    })

# --- بخش منطق رزرو و صندلی‌ها ---

# core/views.py

@login_required                                                                               # اجبار کاربر به ورود قبل از رزرو
def create_reservation(request):
    if request.method == 'POST':
        # ۱. دریافت شناسه‌ها از فرم
        showtime_id_raw = request.POST.get('showtime_id')
        movie_id_raw = request.POST.get('movie_id')
        seats_raw = request.POST.get('selected_seats_list', '')                               # دریافت لیست صندلی‌های انتخاب شده توسط کاربر

        # ۲. پردازش رشته صندلی‌ها و تبدیل به لیست (مثلاً ["3", "15"])
        selected_seats = [s.strip() for s in seats_raw.split(',') if s.strip()]

        if not selected_seats:
            messages.error(request, "لطفاً حداقل یک صندلی انتخاب کنید.")
            return redirect('core:movie_list')

        try:
            # ۳. تبدیل شناسه سانس به عدد (تکی)
            st_id = int(showtime_id_raw)

            # ۴. فراخوانی سرویس رزرو
            # (ایده: در لایه سرویس، ما لیست را می‌فرستیم و آنجا باید روی تک‌تک صندلی‌ها حلقه بزنیم)
            reservation = reserve_seats(                                                      # واگذاری منطق پیچیده رزرو به لایه Service
                user=request.user,
                showtime_id=st_id,
                seats=selected_seats, # لیست رشته‌ها ارسال می‌شود
                seat_type='NORMAL'
            )
            
            messages.success(request, f"رزرو با موفقیت انجام شد. کد پیگیری: {reservation.id}")
            return redirect('core:user_reservations')

        except Exception as e:
            # نمایش دقیق خطا برای عیب‌یابی
            messages.error(request, f"خطا در فرآیند رزرو: {str(e)}")                          # مدیریت خطاهای احتمالی (مثل کمبود موجودی)
            
            # بازگشت هوشمندانه به صفحه انتخاب صندلی در صورت بروز خطا
            try:
                from .models import ShowTime
                st = ShowTime.objects.get(id=int(showtime_id_raw))
                return redirect('core:showtime_detail', cinema_id=st.cinema.id, movie_id=movie_id_raw)
            except:
                return redirect('core:movie_list')
            
    return redirect('core:movie_list')

# --- بخش کاربران و مدیریت ---

def movie_reserve_direct(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    showtimes = ShowTime.objects.filter(movie=movie, start_at__gte=timezone.now())
    if showtimes.exists():
        first_show = showtimes.first()
        return redirect('core:showtime_detail', cinema_id=first_show.cinema.id, movie_id=movie.id)
    messages.warning(request, "سانسی برای این فیلم پیدا نشد.")
    return redirect('core:cinema_list')

@login_required
def user_reservations(request):
    reservations = Reservation.objects.filter(user=request.user).order_by('-created_at')       # نمایش تاریخچه رزروهای کاربر جاری
    return render(request, 'core/my_tickets.html', {'reservations': reservations})

@login_required
def ticket_detail(request, tracking_code):
    reservation = get_object_or_404(Reservation, tracking_code=tracking_code, user=request.user)
    return render(request, 'booking/success.html', {'reservation': reservation})              # نمایش جزئیات بلیط نهایی شده

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:                                                             # کنترل سطح دسترسی ادمین
        return redirect('core:home')
    return render(request, 'admin/dashboard.html')