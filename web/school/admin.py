from django.contrib import admin
from .models import School, Witness


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ["legal_name", "name", "cnpj", "created_date", "letterhead"]
    search_fields = ["name", "legal_name", "cnpj"]
    list_filter = ["tenant"]
    list_display_links = ("legal_name",)


@admin.register(Witness)
class WitnessAdmin(admin.ModelAdmin):
    pass
