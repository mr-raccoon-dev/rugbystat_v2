from django.contrib import admin

from clippings.admin import DropdownFilter
from .models import Person, PersonSeason, Team, Stadium, City


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


class PersonSeasonInline(admin.TabularInline):
    model = PersonSeason
    extra = 1


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = ('name', 'first_name', )
    list_filter = (
        ('year', DropdownFilter),
    )
    fieldsets = (
        (None, {
            'fields': ('name', 'first_name', 'middle_name', )
            }
        ),
        (None, {
            'fields': ('story',)
            }
        ),
        (None, {
            'fields': (('year', 'dob',), ('year_death', 'dod',), 'is_dead')
            }
        ),
    )
    inlines = [
        PersonSeasonInline,
    ]


@admin.register(PersonSeason)
class PersonSeasonAdmin(admin.ModelAdmin):
    search_fields = ('person__name', 'person__first_name', )
    list_display = ('__str__', 'role',)
    list_select_related = ('person', )
    list_filter = (
        ('person__name', DropdownFilter),
        ('year', DropdownFilter),
        ('team__name', DropdownFilter),
    )
