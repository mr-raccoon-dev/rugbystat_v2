from django.contrib import admin

from clippings.admin import DropdownFilter
from .models import Person, Team, Stadium, City


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', )


@admin.register(Stadium)
class StadiumAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', )
    list_select_related = ('city', )
    list_filter = (
        ('city__name', DropdownFilter),
    )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'city', )
    list_select_related = ('city', )
    list_filter = (
        ('city__name', DropdownFilter),
        ('year', DropdownFilter),
    )
    search_fields = ('short_name', )


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = ('name', 'first_name', )
    list_filter = (
        ('year', DropdownFilter),
    )
