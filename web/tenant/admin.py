from django.contrib import admin
from .models import Tenant


class TenantAdmin(admin.ModelAdmin):
    list_display = ["name", "ged_url"]

    fieldsets = (
        (None, {"fields": ("name", "subdomain_prefix",)}),
        (
            "Ged",
            {
                "fields": (
                    "ged_name",
                    "ged_url",
                    "ged_token",
                    "ged_database",
                    "ged_database_user",
                    "ged_database_user_password",
                    "ged_database_host",
                    "ged_database_port",
                    "ged_database_database_engine",
                )
            },
        ),
        (
            "GED - Storage",
            {
                "fields": (
                    "ged_storage_provider",
                    "ged_storage_access_key",
                    "ged_storage_secret_key",
                    "ged_storage_bucket_name",
                    "ged_storage_default_acl",
                    "ged_storage_endpoint_url",
                    "ged_storage_region_name",
                )
            },
        ),
    )


admin.site.register(Tenant, TenantAdmin)
