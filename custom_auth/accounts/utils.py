import secrets
from datetime import timedelta
from django.utils import timezone

def generate_session_key():
    """Генерация уникального ключа сессии"""
    return secrets.token_urlsafe(32)

def get_expiration_time(hours=24):
    """Время окончания сессии"""
    return timezone.now() + timedelta(hours=hours)
