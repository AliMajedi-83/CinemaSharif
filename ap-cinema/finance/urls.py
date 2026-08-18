from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.WalletView.as_view(), name='wallet'),
    path('deposit/', views.deposit_view, name='wallet_deposit'), # آدرس فرم شارژ
]