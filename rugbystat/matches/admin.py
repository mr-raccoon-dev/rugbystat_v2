from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin

from main.filters import DropdownFilter, DateEndListFilter
from teams.models import TeamSeason
from teams.moderator import NoModerationAdmin
from .forms import GroupForm, MatchForm
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

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        field = super(GroupInline, self).formfield_for_manytomany(
            db_field, request, **kwargs
        )
        # get only the teams from THAT season
        field.queryset = field.queryset.filter(
            season=request.resolver_match.args[0]
        )
        return field

@admin.register(Season)
class SeasonAdmin(NoModerationAdmin):
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

    def add_view(self, request, form_url='', extra_context=None):
        self.inlines = (TeamSeasonInline, )
        return super().add_view(request, form_url, extra_context)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'date_start', 'date_end', 'city', 'season')
    list_select_related = ('season', 'city', )
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
class MatchAdmin(NoModerationAdmin, MarkdownxModelAdmin):
    change_form_template = 'admin/matches/match_changeform.html'
    form = MatchForm
    list_display = ('__str__', 'date', 'date_unknown', 'tourn_season')
    list_select_related = ('tourn_season', )
    fieldsets = (
        (None, {'fields': ('name',)}),
        (None, {'fields': (('tourn_season', 'date'), )}),
        (None, {'fields': ('home', 'away', )}),
        (None, {'fields': (('home_score', 'away_score',),
                           ('home_halfscore', 'away_halfscore',), )}),
    )

    def response_change(self, request, obj):
        """Check for custom button request."""
        if 'update-name' in request.POST:
            obj.update_match_name().save()
        return super().response_change(request, obj)
