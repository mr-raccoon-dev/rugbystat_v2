from django.contrib import admin
from teams.models import Person, Team, Stadium, City


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass

@admin.register(Stadium)
class StadiumAdmin(admin.ModelAdmin):
    pass

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    pass

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass
