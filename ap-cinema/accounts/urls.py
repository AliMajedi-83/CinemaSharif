from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('register/', views.register_view, name='register'), # این خط آپدیت شد
    path('logout/', views.custom_logout, name='logout'),
    path('check-phone/', views.check_phone, name='check_phone'),
]