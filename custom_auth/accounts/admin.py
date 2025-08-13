from django.contrib import admin
from django.contrib.admin import AdminSite
from .models import User, Role, BusinessElement, AccessRoleRule, UserSession
from django.utils.html import format_html

# Кастомизация заголовка админки
class CustomAdminSite(AdminSite):
    site_header = "Custom Auth Administration"
    site_title = "Custom Auth Admin"
    index_title = "Welcome to Custom Auth Portal"

custom_admin_site = CustomAdminSite(name='custom_admin')

# Кастомизация отображения пользователей
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'get_full_name', 'role', 'is_active', 'last_login')
    list_filter = ('is_active', 'role', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'last_login')
    fieldsets = (
        (None, {
            'fields': ('email', 'password_hash')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'patronymic')
        }),
        ('Permissions', {
            'fields': ('role', 'is_active')
        }),
        ('Important dates', {
            'fields': ('created_at', 'last_login')
        }),
    )
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name or ''}".strip()
    get_full_name.short_description = 'Full Name'

# Кастомизация отображения ролей
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_short')
    search_fields = ('name', 'description')
    
    def description_short(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'

# Кастомизация отображения правил доступа
class AccessRoleRuleAdmin(admin.ModelAdmin):
    list_display = (
        'role', 
        'element', 
        'read_permission', 
        'create_permission', 
        'update_permission', 
        'delete_permission',
        'permissions_display'
    )
    list_filter = ('role', 'element')
    list_editable = (
        'read_permission', 
        'create_permission', 
        'update_permission', 
        'delete_permission'
    )
    
    def permissions_display(self, obj):
        perms = []
        if obj.read_permission: perms.append("Read")
        if obj.create_permission: perms.append("Create")
        if obj.update_permission: perms.append("Update")
        if obj.delete_permission: perms.append("Delete")
        return ", ".join(perms) or "No permissions"
    permissions_display.short_description = 'Permissions Summary'

# Кастомизация отображения сессий
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key_short', 'ip_address', 'created_at', 'expires_at', 'is_active_display')
    list_filter = ('user', 'created_at')
    readonly_fields = ('session_key', 'user_agent', 'created_at')
    
    def session_key_short(self, obj):
        return f"{obj.session_key[:10]}..." if obj.session_key else ""
    session_key_short.short_description = 'Session Key'
    
    def is_active_display(self, obj):
        return obj.is_active()
    is_active_display.boolean = True
    is_active_display.short_description = 'Is Active'


admin.site.register(User, UserAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(BusinessElement)
admin.site.register(AccessRoleRule, AccessRoleRuleAdmin)
admin.site.register(UserSession, UserSessionAdmin)