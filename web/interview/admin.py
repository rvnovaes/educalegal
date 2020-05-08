from django.contrib import admin

from .models import Interview, InterviewDocumentType, ServerConfig


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
    readonly_fields = ["base_url"]


@admin.register(InterviewDocumentType)
class InterviewDocumentTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(ServerConfig)
class ServerConfigAdmin(admin.ModelAdmin):
    pass
