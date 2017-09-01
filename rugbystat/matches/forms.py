import re
import datetime
from difflib import SequenceMatcher as SM

from dal import autocomplete
from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Tournament, Season

__author__ = 'krnr'


MONTHS_MAP = {
    'январ': '01',
    'феврал': '02',
    'март': '03',
    'апрел': '04',
    'мая': '05',
    'июн': '06',
    'июл': '07',
    'август': '08', 
    'сентябр': '09',
    'октябр': '10',
    'ноябр': '11',
    'декабр': '12'
}


def find_dates(txt, year):
    """
    Parse "с 5 февраля по 10 мая" to datetime objects
    """
    months = r'({})'.format('|'.join(MONTHS_MAP.keys()))
    esc1 = r' (\d+(?= {}))'.format(months)     # (с ... по ...)
    esc2 = r'(\d+-\d+(?= {}))'.format(months)  # (1-10 ...)
    esc3 = r'в|в конце|в начале {}'.format(months)                # в октябре...

    patterns = [esc1, esc2, esc3]
    dates = [re.findall(pattern, txt) for pattern in patterns]
    if dates:
        # try the first found pattern
        try:
            date_start, date_end = dates[0]
            day, month = date_start
            date_start = datetime.datetime.strptime(
                '{}/{}/{}'.format(day, MONTHS_MAP[month], year), 
                '%d/%m/%Y'
            )
            day, month = date_end
            date_end = datetime.datetime.strptime(
                '{}/{}/{}'.format(day, MONTHS_MAP[month], year), 
                '%d/%m/%Y'
            )
        except ValueError:
            # either ('12-15', 'мая') or 'октябр'
            try: 
                days, month = dates[0][0]
                day_start, day_end = days.split('-')
                date_start = datetime.datetime.strptime(
                    '{}/{}/{}'.format(day_start, MONTHS_MAP[month], year), 
                    '%d/%m/%Y'
                )
                date_end = datetime.datetime.strptime(
                    '{}/{}/{}'.format(day_end, MONTHS_MAP[month], year), 
                    '%d/%m/%Y'
                )
            except ValueError:
                # 'октябр'
                date_start = datetime.datetime.strptime(
                    '{}/{}/{}'.format('05', MONTHS_MAP[month], year), 
                    '%d/%m/%Y'
                )
                date_end = datetime.datetime.strptime(
                    '{}/{}/{}'.format('25', MONTHS_MAP[month], year), 
                    '%d/%m/%Y'
                )
        return date_start, date_end
    else:
        return None, None


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
        season.tourn = tourns.first()
    else:
        if not tourns:
            msg = "No tournaments found"
        else:
            ratios = [SM(None, tourn.name, title).ratio() for tourn in tourns]
            max_tourn = tourns[ratios.index(max(ratios))]
            season.tourn = max_tourn
            msg = "Multiple tournaments found for this title. We suggest: {}".format(
                max_tourn.name)
        messages.add_message(request, messages.INFO, msg)

    for line in rest:
        if line.strip():
            date_start, date_end = find_dates(line, year)
            if date_start and date_end:
                season.date_start = date_start
                season.date_end = date_end
                break

    season.story = "\n".join(rest)
    return season


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


class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = ['name', 'story', 'date_start', 'date_end', 'tourn']
        widgets = {
            'tourn': autocomplete.ModelSelect2(url='autocomplete-tournaments')
        }
