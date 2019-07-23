from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin

from main.filters import DropdownFilter
# from .forms import TeamSeasonForm
from .models import (Person, PersonSeason, Team, TeamName, TeamSeason, Stadium, City,
                     TagObject, )
from .moderator import NoModerationAdmin


@admin.register(TagObject)
class TagAdmin(admin.ModelAdmin):
    list_select_related = ('team', 'tournament', 'season', 'match', 'person',)
    search_fields = ('name', )


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


class TeamNameInline(admin.TabularInline):
    model = TeamName
    extra = 1


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'city', )
    list_select_related = ('city', )
    list_filter = (
        ('city__name', DropdownFilter),
        ('year', DropdownFilter),
    )
    search_fields = ('short_name', )
    inlines = (
        TeamNameInline,
    )


@admin.register(TeamName)
class TeamNameAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'team')
    list_select_related = ('team', )
    search_fields = ('__str__', )


@admin.register(TeamSeason)
class TeamSeasonAdmin(NoModerationAdmin):
    # form = TeamSeasonForm

    search_fields = ('team__name', )
    list_display = ('__str__', 'season', 'team')
    list_select_related = ('season', 'team')
    list_filter = (
        ('team__name', DropdownFilter),
        ('year', DropdownFilter),
        ('season__name', DropdownFilter),
    )
    raw_id_fields = ('team', 'season')
    fieldsets = (
        (
            None,
            {
                'fields': ('name', 'year', )
            }
        ),
        (
            None,
            {
                'fields': ('team', 'season', )
            }
        ),
        (
            None,
            {
                'fields': ('place', 'played', 'wins', 'draws', 'losses', 'points',
                           'score')
            }
        ),
        (
            None,
            {
                'fields': ('story',)
            }
        ),
    )


class PersonSeasonInline(admin.TabularInline):
    model = PersonSeason
    extra = 1
    raw_id_fields = ('team', )


@admin.register(Person)
class PersonAdmin(MarkdownxModelAdmin, NoModerationAdmin):
    search_fields = ('name', 'first_name', )
    list_filter = (
        ('year_birth', DropdownFilter),
    )
    fieldsets = (
        (
            None,
            {
                'fields': ('name', 'first_name', 'middle_name', )
            }
        ),
        (
            None,
            {
                'fields': ('story',)
            }
        ),
        (
            None,
            {
                'fields': (('year_birth', 'dob',),
                           ('year_death', 'dod',), 'is_dead')
            }
        ),
    )
    inlines = [
        PersonSeasonInline,
    ]
    admin_integration_enabled = False


@admin.register(PersonSeason)
class PersonSeasonAdmin(NoModerationAdmin):
    search_fields = ('person__name', 'person__first_name', )
    list_display = ('__str__', 'role', 'team', 'season')
    list_select_related = ('person', 'team', 'season')
    list_filter = (
        ('person__name', DropdownFilter),
        ('year', DropdownFilter),
        ('team__name', DropdownFilter),
    )
    raw_id_fields = ('team', 'person', 'season')
