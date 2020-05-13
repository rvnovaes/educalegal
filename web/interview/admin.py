from django.contrib import admin

from .models import Interview, InterviewDocumentType, InterviewServerConfig


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = [
        "name",
        "version",
        "document_type",
        "date_available",
        "list_tenants",
    ]
    filter_horizontal = ["tenants"]
    fields = [
        "name",
        "document_type",
        "version",
        "date_available",
        "description",
        "language",
        "custom_file_name",
        "yaml_name",
        "base_url",
        "interview_server_config",
        "is_generic",
        "is_freemium",
        "use_bulk_interview",
        "tenants"
    ]


@admin.register(InterviewDocumentType)
class InterviewDocumentTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(InterviewServerConfig)
class ServerConfigAdmin(admin.ModelAdmin):
    pass
