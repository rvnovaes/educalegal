from django.contrib import admin
from .models import Plan


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

    fields = [
        "name",
        "value",
        "use_esignature",
        "document_limit",
        "plan_type",
        "use_esignature",
        "use_ged",
        "use_bulk_interview"
    ]

