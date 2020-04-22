from django.contrib import admin
from .models import Tenant, TenantGedData, TenantESignatureData


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ["name"]
    fields = ["name", "subdomain_prefix", "use_esignature", "use_ged", "eua_agreement"]


@admin.register(TenantGedData)
class TenantGedDataAdmin(admin.ModelAdmin):
    list_display = ["tenant", "url"]


@admin.register(TenantESignatureData)
class TenantESignatureDataAdmin(admin.ModelAdmin):
    list_display = ["tenant", "provider"]
