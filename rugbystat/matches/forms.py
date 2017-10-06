from django import forms

from utils.parsers import parse_season
from utils.widgets import ModelSelect2Bootstrap
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
        fields = ['name', 'comment', 'season', 'date_start', 'date_end', 'teams']  # noqa
        widgets = {
            'teams': ModelSelect2Bootstrap(url='autocomplete-teamseasons')
        }


class MatchForm(forms.ModelForm):
    name = forms.CharField(required=False)

    class Meta:
        model = Match
        fields = ('name', 'tourn_season', 'date', 'home', 'away', 'home_score',
                  'away_score', 'home_halfscore', 'away_halfscore', 'story')
        widgets = {
            'home': ModelSelect2Bootstrap(url='autocomplete-teamseasons',
                                          forward=['tourn_season']),
            'away': ModelSelect2Bootstrap(url='autocomplete-teamseasons',
                                          forward=['tourn_season']),
        }


class ImportForm(forms.Form):
    input = forms.CharField(
        strip=False,
        widget=forms.Textarea(attrs={'cols': 80, 'rows': 10})
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ImportForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = super(ImportForm, self).clean()
        self.season = parse_season(data['input'], self.request)
