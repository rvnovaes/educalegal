from django.contrib import admin

from .models import Interview


class InterviewAdmin(admin.ModelAdmin):
    list_display = ("tenant", "name", "version", "date_available")
    list_display_links = ("name",)
    list_filter = ("tenant", "name")


admin.site.register(Interview, InterviewAdmin)
