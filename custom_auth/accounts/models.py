# models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

class Role(models.Model):
    """
    Модель ролей пользователей (админ, модератор, пользователь и т.д.)
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class User(models.Model):
    """
    Кастомная модель пользователя с дополнительными полями
    """
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=128)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.email} ({self.role})"

    def set_password(self, raw_password):
        """Хеширование пароля перед сохранением"""
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        """Проверка пароля"""
        return check_password(raw_password, self.password_hash)

class BusinessElement(models.Model):
    """
    Элементы системы, для которых настраиваются права доступа
    (например: 'user', 'post', 'comment')
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class AccessRoleRule(models.Model):
    """
    Правила доступа ролей к элементам системы
    """
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="access_rules")
    element = models.ForeignKey(BusinessElement, on_delete=models.CASCADE)

    # Права доступа
    read_permission = models.BooleanField(default=False)
    create_permission = models.BooleanField(default=False)
    update_permission = models.BooleanField(default=False)
    delete_permission = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'element')  # Одна роль - один набор прав на элемент

    def __str__(self):
        return f"{self.role.name} -> {self.element.name}"

class UserSession(models.Model):
    """
    Модель для хранения активных сессий пользователей
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_active(self):
        """Проверка активности сессии"""
        return self.expires_at > timezone.now()

    def __str__(self):
        return f"Session for {self.user.email}"