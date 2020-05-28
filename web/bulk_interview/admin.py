from django.contrib import admin

from .models import BulkGeneration


@admin.register(BulkGeneration)
class BulkGenerationAdmin(admin.ModelAdmin):
    pass

