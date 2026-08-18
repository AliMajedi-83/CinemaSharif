# core/urls.py

from django.urls import path
from . import views
from . import admin_views

app_name = 'core'

urlpatterns = [
    # --- مسیرهای مشتری (Client Side) ---
    path('', views.home, name='home'),
    path('cinemas/', views.cinema_list, name='cinema_list'),
    path('movies/', views.movie_list, name='movie_list'),
    path('movies/<int:cinema_id>/', views.movie_list, name='movie_list_by_cinema'),
    
    # (تغییر): اضافه شدن مسیر برای مشاهده صندلی‌ها قبل از رزرو نهایی
    
    # (اصلاح): مسیر ثبت نهایی رزرو (ارسال فرم POST)
    path('reserve/submit/', views.create_reservation, name='create_reservation'),
    
    path('my-tickets/', views.user_reservations, name='user_reservations'),
    path('ticket/<str:tracking_code>/', views.ticket_detail, name='ticket_detail'),
    path('movie/reserve/<int:movie_id>/', views.movie_reserve_direct, name='movie_reserve_direct'),

    # --- پنل مدیریت (Dashboard) ---
    path('dashboard/', admin_views.admin_dashboard, name='dashboard'),
    
    # مدیریت سینماها (Upsert)
    path('dashboard/cinemas/', admin_views.admin_cinema_mgmt, name='admin_cinema_mgmt'),
    path('dashboard/cinemas/create/', admin_views.admin_cinema_upsert, name='admin_cinema_create'),
    path('dashboard/cinemas/edit/<int:cinema_id>/', admin_views.admin_cinema_upsert, name='admin_cinema_edit'),
    path('dashboard/cinemas/delete/<int:cinema_id>/', admin_views.admin_cinema_delete, name='admin_cinema_delete'),

    # مدیریت فیلم‌ها (Upsert)
    path('dashboard/movies/', admin_views.admin_movie_mgmt, name='admin_movie_mgmt'),
    path('dashboard/movies/create/', admin_views.admin_movie_upsert, name='admin_movie_create'),
    path('dashboard/movies/edit/<int:movie_id>/', admin_views.admin_movie_upsert, name='admin_movie_edit'),
    path('dashboard/movies/delete/<int:movie_id>/', admin_views.admin_movie_delete, name='admin_movie_delete'),

    # مدیریت سانس‌ها
    path('dashboard/screenings/', admin_views.admin_screening_mgmt, name='admin_screening_mgmt'),
    path('dashboard/screenings/create/', admin_views.admin_screening_create, name='admin_screening_create'),
    path('dashboard/screenings/delete/<int:screening_id>/', admin_views.admin_screening_delete, name='admin_screening_delete'),
    path('showtime/<int:cinema_id>/<int:movie_id>/', views.showtime_detail, name='showtime_detail'),
]