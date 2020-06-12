import logging

from dal import autocomplete
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views.generic import (CreateView, ListView, DetailView,
                                  YearArchiveView)

from matches.forms import TableImportForm, GroupImportForm, ImportForm, SeasonForm, MatchForm
from teams.models import TeamSeason

from .models import Tournament, Season, Match

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
            names = {s.team_id: s.name for s in seasons}
            for season in seasons:
                if isinstance(season, TeamSeason):
                    season.name = None
                else:
                    save_matches = True

                try:
                    season.save()
                except (IntegrityError, ObjectDoesNotExist, ValueError) as exc:
                    logger.error(f'Cant save {vars(season)}. {exc}')

            if save_matches:
                default_date = season.group.date_start
                display_date = default_date.strftime('%Y-%m-xx')
                for match in matches:
                    try:
                        instance = match.build(date=default_date, date_unknown=display_date)
                        teams = (names[match.home_id], names[match.away_id])
                        instance.display_name = instance._get_name_from_score(teams)
                        instance.name = "{} {}".format(display_date, instance.display_name)
                        instance.save()
                    except IntegrityError:
                        logger.error(f'Cant save {vars(match)}')

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
