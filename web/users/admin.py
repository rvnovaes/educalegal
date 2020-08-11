from django.contrib import admin
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    list_display = (
        "tenant",
        "first_name",
        "last_name",
        "email",
        "force_password_change",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    list_display_links = ("email",)
    list_editable = (
        "force_password_change",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    list_filter = (
        "tenant",
        "is_staff",
        "is_active",
        "is_superuser",
    )

    fieldsets = (
        (None, {"fields": ("tenant", "username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "force_password_change",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
