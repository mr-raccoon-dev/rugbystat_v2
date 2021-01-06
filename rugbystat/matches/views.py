import logging

from dal import autocomplete
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views.generic import (CreateView, ListView, DetailView,
                                  YearArchiveView)

from teams.models import TeamSeason

from .forms import TableImportForm, GroupImportForm, ImportForm, SeasonForm, MatchForm
from .models import Tournament, Season, Group, Match

logger = logging.getLogger('rugbystat')


class TournamentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # if not self.request.user.is_authenticated():
        #     return Season.objects.none()

        qs = Tournament.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class SeasonAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # if not self.request.user.is_authenticated():
        #     return Season.objects.none()

        qs = Season.objects.all()

        year = self.forwarded.get('year', None)
        if year:
            qs = qs.filter(Q(date_end__year=year) |
                           Q(date_start__year=year))

        if self.q:
            for search_term in self.q.split(' '):
                qs = qs.filter(name__icontains=search_term)

        return qs


def import_seasons(request):
    obj_form = SeasonForm()
    status = None

    if request.method == 'POST':
        form = ImportForm(request.POST, request=request)

        if form.is_valid():
            status = 'OK'
            obj_form = SeasonForm(instance=form.season)
        else:
            status = 'False'
    else:
        form = ImportForm()
    return render(request,
                  'import.html',
                  {
                      'form': form,
                      'status': status,
                      'obj_form': obj_form
                  })


def import_table(request):
    if request.method == 'POST':
        if 'group' in request.POST:
            cls = GroupImportForm
        else:
            cls = TableImportForm
        form = cls(request.POST, request=request)
        if form.is_valid():
            seasons, matches = form.table_data
            save_matches = False
            if not seasons and matches:
                save_matches = True

            order = 0
            for season in seasons:
                order += 1
                if isinstance(season, TeamSeason):
                    season.name = None
                    season.order = order
                else:
                    save_matches = True
                    ts = season.group.season.standings.filter(team_id=season.team_id).first()
                    if not ts:
                        ts = TeamSeason(
                            team_id=season.team_id,
                            name=season.name,
                            display_name=f"{season.name}, {season.group.season}",
                            season=season.group.season,
                            has_position=False,
                            show_group=True,
                            order=order,
                        )
                        ts.save()
                    season.group.teams.add(ts)

                try:
                    season.save()
                except (IntegrityError, ObjectDoesNotExist, ValueError) as exc:
                    logger.error(f'Cant save {vars(season)}. {exc}')

            if save_matches:
                if not seasons:  # if no GroupSeason passed, let's look for TeamSeason
                    seasons = Group.objects.get(pk=form.data['group']).season.standings.all()

                names = {s.team_id: s.name for s in seasons}
                for match in matches:
                    try:
                        if not isinstance(match, Match):
                            default_date = season.group.date_start
                            display_date = default_date.strftime('%Y-%m-xx')

                            instance = match.build(date=default_date, date_unknown=display_date)
                        else:
                            instance = match
                            display_date = instance.date_unknown if instance.date_unknown else instance.date.strftime('%Y-%m-%d')

                        teams = (names[match.home_id], names[match.away_id])
                        instance.display_name = instance._get_name_from_score(teams)
                        instance.name = "{} {}".format(display_date, instance.display_name)
                        instance.save()
                    except IntegrityError as exc:
                        logger.error(f'Cant save {vars(match)}')
                        logger.error(str(exc))

            return redirect(form.season)
        else:
            print(form.errors)
    return render(request, 'import.html', {'form': form})


class SeasonCreateView(CreateView):
    model = Season
    form_class = SeasonForm
    success_url = reverse_lazy('import_seasons')


class SeasonYearView(YearArchiveView):
    model = Season
    date_field = 'date_end'
    ordering = ('tourn', 'date_start')
    make_object_list = True


class TournamentListView(ListView):
    """Base list of all Tournaments"""
    model = Tournament
    queryset = Tournament.objects.prefetch_related('seasons')

    def get_context_data(self, **kwargs):
        ctx = super(TournamentListView, self).get_context_data(**kwargs)
        ctx['ends'] = Season.objects.dates('date_end', 'year')
        return ctx


class TournamentDetailView(DetailView):
    """List of all Tournament Seasons"""
    model = Tournament


class SeasonDetailView(DetailView):
    """Detail of one tournament Season"""
    model = Season

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['match_form'] = MatchForm(initial={'tourn_season': ctx['object']})
        ctx['import_form'] = TableImportForm(initial={'season': ctx['object']})
        ctx['documents'] = self.object.documents.with_source_title()

        qs = Season.objects.filter(tourn=self.object.tourn)
        ctx['prev'] = qs.filter(date_end__lt=self.object.date_end).last()
        ctx['next'] = qs.filter(date_end__gt=self.object.date_end).first()
        return ctx


class MatchDetailView(DetailView):
    """Details of one Match"""
    model = Match

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['documents'] = self.object.documents.with_source_title()
        return ctx
