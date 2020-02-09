from django.contrib import admin
from .models import Tenant


class TenantAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "unique_id",
        "ged_url"
    ]


admin.site.register(Tenant, TenantAdmin)
