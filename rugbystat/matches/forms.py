import re

from dal import autocomplete
from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Tournament, Season

__author__ = 'krnr'


def parse_season(data, request):
    YEAR = re.compile(r"""(^\D*)    # all but digits - tournament name
                      ([\d/-]{4,9}) # '1975' or '1975/77' or '1999/2001'
                      *$            # 0 or once""", re.X)

    season = Season()
    first, *rest = data.split('\n')
    # first line denotes title
    title, year = re.match(YEAR, first.strip()).group(1,2)
    season.name = title.strip()
    season.year = year
    tourns = Tournament.objects.filter(name__icontains=season.name)
    if tourns.count() == 1:
        season.tournament = tourns.first()
    else:
        if not tourns:
            msg = "No tournaments found"
        else:
            msg = "Tournaments found for this title: {}".format(
                ", ".join(tourn.name for tourn in tourns)
            )
        messages.add_message(request, messages.INFO, msg)

    season.story = "\n".join(rest)
    print(season.__dict__)


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
        parse_season(data['input'], self.request)


class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = ['name', 'story', 'date_start', 'date_end', 'tourn']
        widgets = {
            'tourn': autocomplete.ModelSelect2(url='autocomplete-tournaments')
        }
