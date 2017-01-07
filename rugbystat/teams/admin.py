from django.contrib import admin
from teams.models import Person, Team, Stadium, City


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass


@admin.register(Stadium)
class StadiumAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', )
    list_select_related = ('city', )
    list_filter = ('city', )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'city', )
    list_select_related = ('city', )
    list_filter = ('city', 'year', )
    search_fields = ('short_name', )


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = ('name', 'first_name', )
    list_filter = ('year', )
