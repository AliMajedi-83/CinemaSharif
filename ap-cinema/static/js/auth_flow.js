/**
 * مدیریت جریان احراز هویت هوشمند - پروژه سینما شریف
 * وظیفه: اعتبارسنجی کلاینت، مدیریت AJAX و تجربه کاربری (UX)
 */

document.addEventListener('DOMContentLoaded', function() {
    // انتخاب المان‌های فرم از DOM
    const authForm = document.getElementById('auth-form');
    const nextBtn = document.getElementById('next-btn'); // دکمه مرحله اول (ادامه)
    const submitBtn = document.getElementById('submit-btn'); // دکمه نهایی (ورود)
    const phoneInput = document.getElementById('phone-input');
    const passwordSection = document.getElementById('password-section'); // بخش رمز عبور که مخفی است
    const passInput = passwordSection ? passwordSection.querySelector('input') : null;

    if (authForm) {
        /**
         * ۱. مدیریت ارسال فرم (Submit)
         * در مرحله اول استعلام شماره و در مرحله دوم ارسال رمز عبور را کنترل می‌کند.
         */
        authForm.addEventListener('submit', function(e) {
            // اگر هنوز بخش رمز عبور مخفی است، یعنی در مرحله اول هستیم
            if (passwordSection.classList.contains('hidden')) {
                e.preventDefault();
                handlePhoneCheck();
            } else {
                // مرحله دوم: چک کردن طول رمز عبور (الزام صفحه ۴ و ۱۱ PDF)
                if (passInput && passInput.value.length < 8) {
                    e.preventDefault();
                    showToast("خطا: رمز عبور باید حداقل ۸ کاراکتر باشد.", "error");
                    passInput.classList.add('input-error'); // افزودن استایل قرمز (تعریف شده در style.css)
                }
            }
        });

        // اجرای تابع چک شماره با کلیک روی دکمه "ادامه"
        if (nextBtn) {
            nextBtn.addEventListener('click', handlePhoneCheck);
        }

        /**
         * ۲. تابع اصلی بررسی شماره تماس (AJAX)
         * طبق سناریوی پیشنهادی در صفحه ۴ PDF عمل می‌کند
         */
        async function handlePhoneCheck() {
            const phone = phoneInput.value.trim();
            phoneInput.classList.remove('input-error');

            // الف) اعتبارسنجی فرمت شماره (۱۱ رقم با ۰۹)
            if (phone.length !== 11 || !phone.startsWith('09')) {
                showToast("لطفاً شماره موبایل معتبر (۱۱ رقم با ۰۹) وارد کنید.", "error");
                phoneInput.classList.add('input-error');
                return;
            }

            // ب) مدیریت وضعیت بارگذاری (Loading State - تسک ۳)
            const originalBtnText = nextBtn.innerHTML;
            nextBtn.disabled = true;
            nextBtn.innerHTML = '<span class="spinner"></span> در حال استعلام...';

            try {
                // ج) ارسال درخواست به بک‌اِند (طراحی شده در Tech Spec)
                const response = await fetch(`/accounts/check-phone/?phone=${phone}`);
                const data = await response.json();

                if (data.exists) {
                    // شماره موجود است -> نمایش فیلد رمز عبور برای ورود
                    passwordSection.classList.remove('hidden');
                    nextBtn.classList.add('hidden');
                    submitBtn.classList.remove('hidden');
                    showToast("خوش آمدید! لطفاً رمز عبور خود را وارد کنید.");
                    if (passInput) passInput.focus();
                } else {
                    // شماره یافت نشد -> هدایت به صفحه ثبت‌نام
                    showToast("این شماره ثبت نشده است. در حال انتقال به صفحه ثبت‌نام...", "error");
                    setTimeout(() => {
                        window.location.href = `/accounts/register/?phone=${phone}`;
                    }, 1500);
                }
            } catch (error) {
                // مدیریت خطاهای ارتباطی (تسک ۳)
                showToast("خطا در ارتباط با سرور بک‌اِند. لطفاً اینترنت خود را چک کنید.", "error");
                console.error("Fetch Error:", error);
            } finally {
                // اتمام وضعیت بارگذاری
                nextBtn.disabled = false;
                nextBtn.innerHTML = originalBtnText;
            }
        }
    }
});