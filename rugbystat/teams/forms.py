import re

from dal import autocomplete
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from moderation.forms import BaseModeratedObjectForm

from .models import Team, TeamSeason, City, Person, PersonSeason

__author__ = 'krnr'


class TeamForm(BaseModeratedObjectForm):
    """Edit Team attributes"""

    class Meta:
        model = Team
        fields = ('story',
                  'year', 'disband_year', 'year_prefix', 'disband_year_prefix')

    def clean(self):
        data = super(TeamForm, self).clean()
        msg = _("Проверьте годы cуществования")
        if all([data['year'], data['disband_year']]):
            if data['year'] > data['disband_year']:
                raise ValidationError(msg)

        return self.cleaned_data


class TeamSeasonForm(BaseModeratedObjectForm):
    """Edit TeamSeason attributes"""

    class Meta:
        model = TeamSeason
        fields = ('name', 'year', 'team', 'season', 'story',
                  'played', 'wins', 'draws', 'losses', 'points', 'score')

        widgets = {
            'team': autocomplete.ModelSelect2(url='autocomplete-teams'),
            'season': autocomplete.ModelSelect2(url='autocomplete-seasons',
                                                forward=['year'])
        }


class PersonForm(BaseModeratedObjectForm):
    """Edit Person attributes"""
    name = forms.CharField(max_length=32, label=_('Фамилия'))

    class Meta:
        model = Person
        fields = ('name', 'first_name', 'middle_name', 'story',
                  'year_birth', 'dob', 'year_death', 'dod', 'is_dead')

    def clean(self):
        data = super(PersonForm, self).clean()
        msg = _("Проверьте годы жизни")
        if all([data['dod'], data['dob']]):
            if data['dod'] < data['dob']:
                raise ValidationError(msg)

        if all([data['year_death'], data['year_birth']]):
            if data['year_death'] < data['year_birth']:
                raise ValidationError(msg)

        return self.cleaned_data


class PersonSeasonForm(BaseModeratedObjectForm):
    """Edit PersonSeason attributes"""
    story = forms.CharField(label=_('Комментарии'), widget=forms.Textarea)

    class Meta:
        model = PersonSeason
        fields = ('person', 'year', 'role', 'team', 'season', 'story')
        widgets = {
            'season': autocomplete.ModelSelect2(url='autocomplete-seasons',
                                                forward=['year']),
            'team': autocomplete.ModelSelect2(url='autocomplete-teams',
                                              forward=['year'])
        }


def init_date(prefix_year):
    try:
        year = int(prefix_year.strip().split(' ')[-1])
        prefix = prefix_year[:prefix_year.find(str(year))]
    except:
        prefix = prefix_year
        year = None
    return prefix, year


def init_team(line):
    team_and_city, year_create, year_disband, story = re.findall(
                '<li>(.+) \(([^-]*)-*([^-]*)\)(.*)', line)[0]
    city = team_and_city.split(' ')[-1]
    name = team_and_city[:team_and_city.find(city)].strip().strip('<b>')

    city_instance, _ = City.objects.get_or_create(name=city)

    prefix_create, create = init_date(year_create)
    prefix_disband, disband = init_date(year_disband)

    team = Team(name=name, story=story, city=city_instance,
                year=create or None, year_prefix=prefix_create,
                disband_year=disband or None,
                disband_year_prefix=prefix_disband)
    return team


def parse_teams(data):
    previous_team = None
    for line in data.split('\n'):
        if len(line) < 4:
            previous_team.save()
            break
        if line[:4] == '<li>':
            if not previous_team:
                previous_team = init_team(line)
            else:
                previous_team.save()
                previous_team = init_team(line)
        else:
            if previous_team:
                previous_team.story += line


class ImportForm(forms.Form):
    input = forms.CharField(
        strip=False,
        widget=forms.Textarea(attrs={'cols': 80, 'rows': 20})
    )

    def clean(self):
        data = super(ImportForm, self).clean()
        parse_teams(data['input'])
