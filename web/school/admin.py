from django.contrib import admin
from .models import School


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ["name", "cnpj", "legal_name", "created_date", "letterhead"]
    search_fields = ["name", "cnpj"]
    list_filter = ["tenant"]
