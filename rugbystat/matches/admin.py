from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from main.filters import DropdownFilter, DateEndListFilter
from teams.models import TeamSeason
from .forms import GroupForm
from .models import Tournament, Season, Group, Match


@admin.register(Tournament)
class TournamentAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


class TeamSeasonInline(admin.TabularInline):
    model = TeamSeason
    extra = 1
    raw_id_fields = ('team', )
    ordering = ('order', )


class GroupInline(admin.TabularInline):
    model = Group
    extra = 1


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
        GroupInline,
        TeamSeasonInline,
    ]


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_start', 'date_end', 'season')
    list_select_related = ('season', )
    list_filter = (('season__name', DropdownFilter), DateEndListFilter,)
    form = GroupForm
    filter_horizontal = ['teams']

    def get_form(self, request, obj=None, **kwargs):
        self.instance = obj  # Capture instance before the form gets generated
        return super(GroupAdmin, self).get_form(request, obj=obj, **kwargs)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'teams' and self.instance:
            # restrict teams queryset to those related to this season:
            kwargs['queryset'] = self.instance.season.standings.all()
        return super(GroupAdmin, self).formfield_for_manytomany(
            db_field, request=request, **kwargs)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    pass
