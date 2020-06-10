from django.contrib import admin

from .models import BulkInterview


@admin.register(BulkInterview)
class BulkGenerationAdmin(admin.ModelAdmin):
    pass

