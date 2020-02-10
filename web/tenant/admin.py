from django.contrib import admin
from .models import Tenant


class TenantAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "ged_url"
    ]


admin.site.register(Tenant, TenantAdmin)
