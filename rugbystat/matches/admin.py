from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.forms.widgets import TextInput

from main.filters import DropdownFilter, DateEndListFilter
from teams.models import TeamSeason
from .models import Tournament, Season, Match


@admin.register(Tournament)
class TournamentAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


class TeamSeasonInline(admin.TabularInline):
    model = TeamSeason
    extra = 1
    raw_id_fields = ('team', )
    ordering = ('order', )


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_start', 'date_end', 'story')
    list_filter = (
        ('tourn__name', DropdownFilter),
        DateEndListFilter,
    )
    list_select_related = ('tourn', )
    search_fields = ('name', )
    inlines = [
        TeamSeasonInline,
    ]


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    pass
