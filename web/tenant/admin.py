from django.contrib import admin
from .models import Tenant, TenantGedData, ESignatureApp


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ["name", "plan", "esignature_app", "auto_enrolled", "phone", "created_date"]
    list_filter = ["auto_enrolled", "plan"]
    search_fields = ["name"]


@admin.register(TenantGedData)
class TenantGedDataAdmin(admin.ModelAdmin):
    list_display = ["tenant", "url"]


@admin.register(ESignatureApp)
class ESignatureAppAppAdmin(admin.ModelAdmin):
    list_display = ["name", "provider", "test_mode"]

