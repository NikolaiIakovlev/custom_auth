from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Role, User, BusinessElement, AccessRoleRule, Session


# ----------------------------------------
# Действия для User
# ----------------------------------------

def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True)
make_active.short_description = "Активировать выбранных пользователей"

def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)
make_inactive.short_description = "Деактивировать выбранных пользователей"


# ----------------------------------------
# RoleAdmin
# ----------------------------------------

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'user_count')
    search_fields = ('name',)
    ordering = ('name',)

    def user_count(self, obj):
        return obj.user_set.count()

    user_count.short_description = "Количество пользователей"


# ----------------------------------------
# UserAdmin
# ----------------------------------------

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'email', 'role', 'is_active',
        'created_at', 'session_count', 'view_permissions_link'
    )
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('first_name', 'last_name', 'patronymic', 'email')
    readonly_fields = ('created_at', 'password_hash')
    fieldsets = (
        ('Персональная информация', {
            'fields': ('first_name', 'last_name', 'patronymic', 'email')
        }),
        ('Роль и доступ', {
            'fields': ('role', 'is_active')
        }),
        ('Системные данные', {
            'classes': ('collapse',),
            'fields': ('password_hash', 'created_at'),
            'description': "Поля <strong>password_hash</strong> и <strong>created_at</strong> только для чтения."
        }),
    )
    actions = [make_active, make_inactive]
    ordering = ('-created_at',)

    def full_name(self, obj):
        parts = [obj.first_name, obj.last_name or '', obj.patronymic or '']
        return ' '.join(filter(None, parts)).strip()

    full_name.short_description = "ФИО"

    def session_count(self, obj):
        count = obj.session_set.count()
        if count == 0:
            return format_html('<span style="color: gray;">0 сессий</span>')
        return format_html('<span style="color: green;">{} активн{} сессий</span>', count, 'ая' if count == 1 else 'ых')

    session_count.short_description = "Сессии"

    def view_permissions_link(self, obj):
        if not obj.role:
            return format_html('<span style="color: gray;">Нет роли</span>')
        url = reverse('admin:accounts_accessrolerule_changelist') + f'?role__id__exact={obj.role.id}'
        return format_html(
            '<a href="{}" target="_blank">Просмотреть права роли "{}"</a>',
            url, obj.role.name
        )

    view_permissions_link.short_description = "Права доступа"
    view_permissions_link.allow_tags = True


# ----------------------------------------
# BusinessElementAdmin
# ----------------------------------------

class AccessRuleInline(admin.TabularInline):
    model = AccessRoleRule
    extra = 1
    fields = (
        'role',
        'read_permission', 'read_all_permission',
        'create_permission',
        'update_permission', 'update_all_permission',
        'delete_permission', 'delete_all_permission'
    )
    autocomplete_fields = ('role',)
    verbose_name = "Правило доступа"
    verbose_name_plural = "Правила доступа"


@admin.register(BusinessElement)
class BusinessElementAdmin(admin.ModelAdmin):
    list_display = ('name', 'access_rule_count')
    search_fields = ('name',)
    inlines = [AccessRuleInline]
    ordering = ('name',)

    def access_rule_count(self, obj):
        return obj.accessrolerule_set.count()

    access_rule_count.short_description = "Количество правил доступа"


# ----------------------------------------
# AccessRoleRuleAdmin
# ----------------------------------------

@admin.register(AccessRoleRule)
class AccessRoleRuleAdmin(admin.ModelAdmin):
    list_display = (
        'role', 'element',
        'read_permission', 'read_all_permission',
        'create_permission',
        'update_permission', 'update_all_permission',
        'delete_permission', 'delete_all_permission'
    )
    list_filter = ('role', 'element', 'read_permission', 'create_permission', 'update_permission', 'delete_permission')
    search_fields = ('role__name', 'element__name')
    autocomplete_fields = ('role', 'element')
    list_editable = (
        'read_permission', 'read_all_permission',
        'create_permission',
        'update_permission', 'update_all_permission',
        'delete_permission', 'delete_all_permission'
    )
    ordering = ('role__name', 'element__name')


# ----------------------------------------
# SessionAdmin
# ----------------------------------------

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'session_id_truncated', 'created_at', 'expires_at', 'is_valid_display')
    list_filter = ('created_at', 'expires_at', 'user__role')
    search_fields = ('user__email', 'session_id')
    readonly_fields = ('user', 'session_id', 'created_at', 'expires_at')
    ordering = ('-created_at',)

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = "Пользователь"
    user_email.admin_order_field = 'user__email'

    def session_id_truncated(self, obj):
        return obj.session_id[:16] + "..." if len(obj.session_id) > 16 else obj.session_id

    session_id_truncated.short_description = "ID сессии"

    def is_valid_display(self, obj):
        valid = obj.is_valid()
        color = "green" if valid else "red"
        text = "Активна" if valid else "Истекла"
        return format_html('<span style="color: {};">{}</span>', color, text)

    is_valid_display.short_description = "Статус"


# ----------------------------------------
# Заголовки админки
# ----------------------------------------

admin.site.site_header = "Администрирование системы"
admin.site.site_title = "Панель управления"
admin.site.index_title = "Добро пожаловать в систему управления доступом"