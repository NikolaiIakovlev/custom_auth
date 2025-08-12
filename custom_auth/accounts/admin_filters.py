from django.contrib import admin

class IsValidFilter(admin.SimpleListFilter):
    title = 'is valid'
    parameter_name = 'is_valid'

    def lookups(self, request, model_admin):
        return (
            ('valid', 'Valid'),
            ('expired', 'Expired'),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'valid':
            return queryset.filter(expires_at__gt=now)
        if self.value() == 'expired':
            return queryset.filter(expires_at__lte=now)
        return queryset