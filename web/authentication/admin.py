from django.contrib import admin
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email',
                    'is_staff', 'is_active', 'is_superuser', 'is_analyst', 'is_manager', 'is_administrator')
    list_display_links = ('username',)
    list_editable = ('is_staff', 'is_active', 'is_superuser', 'is_analyst', 'is_manager', 'is_administrator')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'is_analyst', 'is_manager', 'is_administrator')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_analyst', 'is_manager', 'is_administrator',
            'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )



admin.site.register(User, CustomUserAdmin)
