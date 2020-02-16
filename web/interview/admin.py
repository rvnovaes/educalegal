from django.contrib import admin

from .models import Interview, InterviewDocumentType


class InterviewAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "date_available")
    list_display_links = ("name",)
    list_filter = ("name",)


class InterviewDocumentTypeAdmin(admin.ModelAdmin):
    pass


admin.site.register(Interview, InterviewAdmin)
admin.site.register(InterviewDocumentType, InterviewDocumentTypeAdmin)
