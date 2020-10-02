from django.contrib import admin
from .models import Plan
from tenant.models import Tenant


class TenantInline(admin.StackedInline):
    model = Tenant
    extra = 0
    exclude = ['name', 'subdomain_prefix', 'eua_agreement', 'auto_enrolled', 'esignature_app', 'phone',
               'esignature_folder', 'webhook_production', 'webhook_sandbox']
    can_delete = False


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = [
        "name",
        "value",
        "use_esignature",
        "use_ged",
        "use_bulk_interview",
    ]
    list_editable = [
        "use_esignature",
        "use_ged",
        "use_bulk_interview"
    ]
    inlines = [
        TenantInline,
    ]
