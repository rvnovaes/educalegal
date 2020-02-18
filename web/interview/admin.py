from django.contrib import admin

from .models import Interview, InterviewDocumentType


class InterviewAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', "version", "date_available", 'list_tenants']
    filter_horizontal = ['tenants']


class InterviewDocumentTypeAdmin(admin.ModelAdmin):
    pass


admin.site.register(Interview, InterviewAdmin)
admin.site.register(InterviewDocumentType, InterviewDocumentTypeAdmin)
