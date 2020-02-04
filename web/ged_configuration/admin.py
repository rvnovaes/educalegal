from django.contrib import admin
from .models import Configuration


class ConfigurationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Configuration, ConfigurationAdmin)