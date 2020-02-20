from django.contrib import admin

from .models import Interview, InterviewDocumentType


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', "version", "date_available", 'list_tenants']
    filter_horizontal = ['tenants']


class InterviewDocumentTypeAdmin(admin.ModelAdmin):
    pass


admin.site.register(InterviewDocumentType, InterviewDocumentTypeAdmin)
