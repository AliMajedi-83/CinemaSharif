from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from .models import Wallet
from finance.utils import credit_wallet

class WalletView(LoginRequiredMixin, DetailView):                             # نمایش جزئیات کیف پول فقط برای کاربران لاگین شده
    model = Wallet
    template_name = 'finance/wallet.html'
    context_object_name = 'wallet'

    def get_object(self):

        wallet, created = Wallet.objects.get_or_create(user=self.request.user)# اطمینان از وجود کیف پول (Lazy Initialization)
        return wallet

def deposit_view(request):                                                    # تابع عملیاتی برای افزایش موجودی (شارژ)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if amount:
            credit_wallet(wallet=request.user.wallet, amount=amount, description='شارژ کیف پول') # فراخوانی تابع کمکی تراکنش
    return redirect('finance:wallet')                                         # بازگشت به صفحه کیف پول پس از اتمام عملیات