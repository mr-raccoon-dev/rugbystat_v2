from dal import autocomplete
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.forms.formsets import formset_factory
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import CreateView, DetailView, UpdateView
from django.views.generic.edit import FormMixin

from .forms import (ImportForm, PersonForm, PersonSeasonForm, TeamForm,
                    PersonRosterForm, ImportRosterForm)
from .models import Person, PersonSeason, Team, TeamSeason


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


class TeamAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # if not self.request.user.is_authenticated():
        #     return Team.objects.none()

        qs = Team.objects.all()

        year = self.forwarded.get('year', None)
        if year:
            qs = qs.filter(Q(year__lte=year, disband_year__gte=year) |
                           Q(year__lte=year, disband_year__isnull=True))

        if self.q:
            qs = qs.filter(Q(short_name__icontains=self.q) |
                           Q(city__name__icontains=self.q))

        return qs


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


class TeamSeasonView(FormMixin, DetailView):
    """List of all matches of a specific Team in a Season"""
    model = TeamSeason
    form_class = ImportRosterForm

    def get_context_data(self, **kwargs):
        kwargs = super(TeamSeasonView, self).get_context_data(**kwargs)
        kwargs['person_form'] = PersonRosterForm(initial=self.get_initial())
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
        return kwargs
