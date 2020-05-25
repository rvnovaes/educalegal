from django.contrib import admin
from .models import Tenant, TenantGedData, TenantESignatureData


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ["name", "plan", "auto_enrolled", "created_date"]
    list_filter = ["auto_enrolled", "plan"]
    list_editable = ["plan"]
    search_fields = ["name"]


@admin.register(TenantGedData)
class TenantGedDataAdmin(admin.ModelAdmin):
    list_display = ["tenant", "url"]


@admin.register(TenantESignatureData)
class TenantESignatureDataAdmin(admin.ModelAdmin):
    list_display = ["tenant", "provider"]
