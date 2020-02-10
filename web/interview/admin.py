from django.contrib import admin

from .models import Interview


class InterviewAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "date_available")
    list_display_links = ("name",)
    list_filter = ("name",)


admin.site.register(Interview, InterviewAdmin)
