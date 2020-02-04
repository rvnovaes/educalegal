from django.contrib import admin
from .models import Configuration

# Register your models here.


class ConfigurationAdmin(admin.ModelAdmin):
    pass


admin.site.register(Configuration, ConfigurationAdmin)
