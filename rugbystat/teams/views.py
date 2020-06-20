import operator
from functools import reduce

from dal import autocomplete
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.forms.formsets import formset_factory
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import CreateView, DetailView, UpdateView
from django.views.generic.edit import FormMixin

from matches.models import Match
from .forms import (ImportForm, PersonForm, PersonSeasonForm, TeamForm, TeamSeasonForm,
                    PersonRosterForm, ImportRosterForm)
from .models import Person, PersonSeason, Team, TeamSeason, TagObject, City


def import_teams(request):
    if request.method == 'POST':
        form = ImportForm(request.POST)
        if form.is_valid():
            return HttpResponse('OK', content_type="text/plain")
        else:
            return HttpResponse('False', content_type="text/plain")
    else:
        form = ImportForm()
    return render(request, 'import.html', {'form': form})


class TagAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = TagObject.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class CityAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = City.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class TeamAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Team.objects.filter()

        year = self.forwarded.get('year', None)
        if year:
            qs = qs.filter(Q(year__lte=year, disband_year__gte=year) |
                           Q(year__lte=year, disband_year__isnull=True))

        if self.q:
            for search_term in self.q.split(' '):
                queries = [
                    Q(**{lookup: search_term})
                    for lookup in (
                        'short_name__istartswith',
                        'names__name__istartswith',
                        'city__name__istartswith',
                    )
                ]
                qs = qs.filter(reduce(operator.or_, queries))

        return qs.distinct()


class TeamSeasonAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = TeamSeason.objects.all()

        season = (self.forwarded.get('season', None) or
                  self.forwarded.get('tourn_season', None))
        if season:
            qs = qs.filter(season=season)

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class TeamBySeasonAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Team.objects.all()

        season = (self.forwarded.get('season', None) or
                  self.forwarded.get('tourn_season', None))
        if season:
            qs = qs.filter(seasons__season=season)

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class PersonSeasonAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = PersonSeason.objects.all()

        season = (self.forwarded.get('season', None) or
                  self.forwarded.get('tourn_season', None))
        if season:
            qs = qs.filter(season=season)

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class PersonBySeasonAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Person.objects.all()

        season = (self.forwarded.get('season', None) or
                  self.forwarded.get('tourn_season', None))
        if season:
            qs = qs.filter(seasons__season=season)

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class TeamUpdateView(UpdateView):
    model = Team
    form_class = TeamForm

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        form = TeamSeasonForm(initial={'team': self.object})
        kwargs['season_form'] = form
        kwargs['seasons'] = self.object.seasons.select_related('season')
        kwargs['documents'] = self.object.documents.with_source_title()
        return kwargs


class TeamSeasonView(FormMixin, DetailView):
    """List of all matches of a specific Team in a Season"""
    model = TeamSeason
    form_class = ImportRosterForm

    def get_context_data(self, **kwargs):
        kwargs = super(TeamSeasonView, self).get_context_data(**kwargs)
        kwargs['person_form'] = PersonRosterForm(initial=self.get_initial())
        kwargs['roster'] = self.object.get_players()
        kwargs['same_year_players'] = PersonSeason.objects.filter(
            team_id=self.object.team_id, year=self.object.year
        ).exclude(
            season_id=self.object.season_id
        ).select_related(
            'person__tagobject_ptr'
        ).order_by('role', 'person__name')

        return kwargs

    def get_initial(self):
        return {'season': self.object.season.pk,
                'team': self.object.team.pk,
                'year': self.object.season.date_end.year}

    def get_form_kwargs(self):
        kwargs = super(TeamSeasonView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        return self.object.get_absolute_url()

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class TeamAllYearView(DetailView):
    """List of all matches of a specific Team in a year"""
    model = Team
    template_name = 'teams/team_year.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object, **kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        year = int(ctx["year"])
        ctx['team_name'] = self.object.get_name_for(year)

        matches = Match.objects.for_team(self.object.pk).filter(date__year=year)
        matches = matches.select_related('tourn_season').order_by('date')
        ctx['matches'] = matches
        return ctx


class PersonCreateView(CreateView):
    model = Person
    form_class = PersonForm
    success_url = reverse_lazy('persons')
    template_name = 'persons.html'


class PersonUpdateView(UpdateView):
    model = Person
    form_class = PersonForm

    def get_context_data(self, **kwargs):
        kwargs = super(PersonUpdateView, self).get_context_data(**kwargs)
        form = PersonSeasonForm(initial={'person': self.object.pk})
        kwargs['season_form'] = form
        kwargs['seasons'] = self.object.seasons.select_related('season', 'team')
        kwargs['documents'] = self.object.documents.with_source_title()
        return kwargs
