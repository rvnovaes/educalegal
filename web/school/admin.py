from django.contrib import admin
from .models import School, Signatory,Grade


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ["legal_name", "name", "cnpj", "created_date", "letterhead"]
    search_fields = ["name", "legal_name", "cnpj"]
    list_filter = ["tenant"]
    list_display_links = ("legal_name",)


@admin.register(Signatory)
class SignatoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    pass
