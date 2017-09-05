from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from main.filters import DropdownFilter, DateEndListFilter
from .models import Tournament, Season, Match


@admin.register(Tournament)
class TournamentAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_start', 'date_end', 'story')
    list_filter = (
        ('tourn__name', DropdownFilter),
        DateEndListFilter,
    )
    list_select_related = ('tourn', )
    search_fields = ('name', )



@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    pass
