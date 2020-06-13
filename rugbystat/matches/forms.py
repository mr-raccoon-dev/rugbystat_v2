from collections import namedtuple

from django import forms

from utils.parsers import parse_season, parse_table, parse_matches
from utils.widgets import ModelSelect2Bootstrap, ModelSelect2MultiBootstrap
from .models import Season, Group, Match

__author__ = 'krnr'


class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = ['name', 'story', 'date_start', 'date_end', 'tourn']
        widgets = {
            'tourn': ModelSelect2Bootstrap(url='autocomplete-tournaments')
        }


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'comment', 'season', 'round_type', 'date_start',
                  'date_end', 'city', 'teams']
        widgets = {
            'city': ModelSelect2Bootstrap(url='autocomplete-cities'),
            'season': ModelSelect2Bootstrap(url='autocomplete-seasons'),
            'teams': ModelSelect2MultiBootstrap(url='autocomplete-teamseasons',
                                                forward=['season']),
        }


class MatchForm(forms.ModelForm):
    name = forms.CharField(required=False)

    class Meta:
        model = Match
        fields = ('name', 'tourn_season', 'date', 'home', 'away', 'home_score',
                  'away_score', 'home_halfscore', 'away_halfscore', 'story')
        widgets = {
            'tourn_season': ModelSelect2Bootstrap(url='autocomplete-seasons'),
            'home': ModelSelect2Bootstrap(url='autocomplete-teamseasons',
                                          forward=['tourn_season']),
            'away': ModelSelect2Bootstrap(url='autocomplete-teamseasons',
                                          forward=['tourn_season']),
        }


class ImportForm(forms.Form):
    raw = forms.CharField(
        strip=False,
        widget=forms.Textarea(attrs={'cols': 80, 'rows': 10})
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ImportForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = super(ImportForm, self).clean()
        self.season = parse_season(data['raw'], self.request)


class TableImportForm(ImportForm):
    season = forms.IntegerField(widget=forms.HiddenInput())

    def clean(self):
        data = super(forms.Form, self).clean()
        season_id = self.request.POST['season']
        group = namedtuple('FakeGroup', 'pk')(None)
        self.season = Season.objects.get(pk=season_id)
        self.table_data = parse_table(data['raw'], self.season, group)


class GroupImportForm(ImportForm):
    group = forms.IntegerField(widget=forms.HiddenInput())

    def clean(self):
        data = super(forms.Form, self).clean()
        group_id = self.request.POST['group']
        group = Group.objects.get(pk=group_id)
        self.season = group.season
        if '<div class="match">' in data['raw'] or "<div class='match'>" in data['raw']:
            self.table_data = parse_matches(data['raw'], self.season, group)
        else:
            self.table_data = parse_table(data['raw'], self.season, group)
