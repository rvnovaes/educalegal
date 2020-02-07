from django.contrib import admin
from .models import GEDConfiguration


class GEDConfigurationAdmin(admin.ModelAdmin):
    pass


admin.site.register(GEDConfiguration, GEDConfigurationAdmin)