import re
import logging
from difflib import SequenceMatcher as SM

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.messages import success
from django.forms import inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from moderation.forms import BaseModeratedObjectForm

from matches.models import Season
from utils.widgets import ModelSelect2Bootstrap
from .models import Team, TeamSeason, City, Person, PersonSeason

__author__ = 'krnr'


logger = logging.getLogger('django.request')


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
            'team': ModelSelect2Bootstrap(url='autocomplete-teams'),
            'season': ModelSelect2Bootstrap(url='autocomplete-seasons',
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
            'season': ModelSelect2Bootstrap(url='autocomplete-seasons',
                                            forward=['year']),
            'team': ModelSelect2Bootstrap(url='autocomplete-teams',
                                          forward=['year'])
        }


class PersonRosterForm(PersonSeasonForm):
    class Meta:
        model = PersonSeason
        fields = ('id', 'person', 'year', 'role', 'team', 'season', 'story')
        widgets = {
            'person': ModelSelect2Bootstrap(url='autocomplete-personseasons'),
            'year': forms.HiddenInput(),
            'season': forms.HiddenInput(),
            'team': forms.HiddenInput(),
        }


# can't get it to work with dal widget (((
PersonSeasonFormSet = inlineformset_factory(Season, PersonSeason,
                                            form=PersonRosterForm, extra=1)


def init_date(prefix_year):
    try:
        year = int(prefix_year.strip().split(' ')[-1])
        prefix = prefix_year[:prefix_year.find(str(year))]
    except:
        prefix = prefix_year
        year = None
    return prefix, year


def init_team(line):
    expr = '<li>(.+) \(([^-]*)-*([^-]*)\)(.*)'
    team_and_city, year_create, year_disband, story = re.findall(expr, line)[0]
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


POSITIONS = {
    '15': PersonSeason.FB,
    '14-11': PersonSeason.BACK,
    '10': PersonSeason.FH,
    '9': PersonSeason.SH,
    '6-8': PersonSeason.BACKROW,
    '4-5': PersonSeason.LOCK,
    '1-3': PersonSeason.FIRST_ROW,
    '14': PersonSeason.WINGER,
    '13': PersonSeason.CENTER,
    '12': PersonSeason.CENTER,
    '12-13': PersonSeason.CENTER,
    '11': PersonSeason.WINGER,
    '9-10': PersonSeason.HALF,
    '8': PersonSeason.BACKROW,
    '7': PersonSeason.BACKROW,
    '6': PersonSeason.BACKROW,
    '5': PersonSeason.LOCK,
    '4': PersonSeason.LOCK,
    '4/5': PersonSeason.LOCK,
    '3': PersonSeason.PROP,
    '2': PersonSeason.HOOKER,
    '1': PersonSeason.PROP,
    '1/3': PersonSeason.PROP,
    '1-8': PersonSeason.FORWARD,
    '15-9': PersonSeason.BACK,
}


def parse_rosters(request, data):
    input_ = data['input'].replace('\r\n', ' ').replace(' / ', ';')
    positions = input_.strip().split(";")
    for position in positions:
        # split number from names
        esc = r'(\d{1,2}-*\d{0,2}).(.*)'
        try:
            print("Checking {}".format(position))
            number, players = re.findall(esc, position)[0]
        except ValueError:
            msg = "Couldn't import data: {}".format(position)
            print(msg)
            logger.warning(msg)
        else:
            role = POSITIONS.get(number, PersonSeason.PLAYER)
            for player in players.split(','):
                # find person
                try:
                    first_name, name = player.split()
                except ValueError:
                    msg = "Couldn't split: {}".format(player)
                    print(msg)
                    logger.warning(msg)

                    name = player

                persons = Person.objects.filter(name=name)
                # what if there're multiple?
                print("Finding best match from {}".format(persons))

                person = find_best_match(persons, name, first_name)
                print("Found {}".format(person))

                # get_or_create PersonSeason for number
                obj, created = PersonSeason.objects.get_or_create(
                    role=role, person=person, season_id=data['season'],
                    team_id=data['team'], year=data['year']
                )
                if created:
                    success(request, "Created {}".format(obj))
                else:
                    success(request, "Found {}".format(obj))


def find_best_match(queryset, name, first_name, all=False):
    """
    Find the most suitable instance by SequenceMatcher from queryset.

    If None found, try to look for all objects.
    If again None found - create one.
    """
    ratios = [SM(None, str(obj), "{} {}".format(first_name, name)).ratio()
              for obj in queryset]

    if ratios and max(ratios) > 0.6:
        found = queryset[ratios.index(max(ratios))]
    elif all:
        found = Person.objects.create(name=name, first_name=first_name)
    else:
        queryset = Person.objects.all()
        found = find_best_match(queryset, name, first_name, all=True)
    return found


class ImportRosterForm(forms.Form):
    input = forms.CharField(
        strip=True,
        widget=forms.Textarea(attrs={'cols': 80, 'rows': 20})
    )
    season = forms.IntegerField(widget=forms.HiddenInput())
    year = forms.IntegerField(widget=forms.HiddenInput())
    team = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(ImportRosterForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = super(ImportRosterForm, self).clean()
        parse_rosters(self.request, data)
