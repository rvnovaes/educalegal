from django.contrib import admin
from .models import City, Country, School, State


class CityAdmin(admin.ModelAdmin):
    pass


class CountryAdmin(admin.ModelAdmin):
    pass


class SchoolAdmin(admin.ModelAdmin):
    pass


class StateAdmin(admin.ModelAdmin):
    pass


admin.site.register(City, CityAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(State, StateAdmin)
