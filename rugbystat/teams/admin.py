from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from moderation.admin import ModerationAdmin

from clippings.admin import DropdownFilter
from .forms import TeamSeasonForm
from .models import Person, PersonSeason, Team, TeamSeason, Stadium, City


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


@admin.register(TeamSeason)
class TeamSeasonAdmin(admin.ModelAdmin):
    form = TeamSeasonForm

    search_fields = ('team__name', )
    list_display = ('__str__', 'season', 'team')
    list_select_related = ('season', 'team')
    list_filter = (
        ('team__name', DropdownFilter),
        ('year', DropdownFilter),
        ('season__name', DropdownFilter),
    )
    # raw_id_fields = ('team', 'season')


class PersonSeasonInline(admin.TabularInline):
    model = PersonSeason
    extra = 1
    raw_id_fields = ('team', )


@admin.register(Person)
class PersonAdmin(ModerationAdmin, MarkdownxModelAdmin):
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
    list_display = ('__str__', 'role', 'team')
    list_select_related = ('person', 'team')
    list_filter = (
        ('person__name', DropdownFilter),
        ('year', DropdownFilter),
        ('team__name', DropdownFilter),
    )
    raw_id_fields = ('team', )
