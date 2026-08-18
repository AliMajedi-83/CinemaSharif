# core/db/transactions.py
from contextlib import contextmanager
from django.db import transaction
from django.db import models

@contextmanager
def atomic():
    """
    Wrapper around Django transaction.atomic to keep usage consistent.
    """
    with transaction.atomic():
        yield

        
def get_object_for_update(qs: models.QuerySet, **filters):
    """
    qs: مثلا ShowTime.objects
    این تابع رکورد رو با SELECT ... FOR UPDATE قفل می‌کنه.
    """
    return qs.select_for_update().get(**filters)
