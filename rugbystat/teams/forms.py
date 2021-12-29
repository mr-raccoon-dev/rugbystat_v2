from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.utils.translation import ugettext_lazy as _

from clippings.models import Document
from matches.models import Season
from utils.widgets import ModelSelect2Bootstrap
from utils.parsers import parse_alphabet, parse_rosters, parse_teams
from .models import Team, TeamSeason, Person, PersonSeason

__author__ = 'krnr'


class TagThroughForm(forms.ModelForm):
    class Meta:
        model = Document.tag.through
        fields = ('tagobject', )
        widgets = {
            'tagobject': ModelSelect2Bootstrap(url='autocomplete-tags')
        }


class TeamForm(forms.ModelForm):
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


class TeamSeasonForm(forms.ModelForm):
    """Edit TeamSeason attributes"""

    class Meta:
        model = TeamSeason
        fields = ('name', 'year', 'team', 'season', 'story',
                  'place', 'played', 'wins', 'draws', 'losses', 'points', 'score')

        widgets = {
            'team': ModelSelect2Bootstrap(url='autocomplete-teams'),
            'season': ModelSelect2Bootstrap(url='autocomplete-seasons')
        }


TeamSeasonFormSet = inlineformset_factory(Season, TeamSeason,
                                          form=TeamSeasonForm, extra=1)


class PersonForm(forms.ModelForm):
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


class PersonSeasonForm(forms.ModelForm):
    """Edit PersonSeason attributes"""
    story = forms.CharField(label=_('Комментарии'), widget=forms.Textarea, required=False)

    class Meta:
        model = PersonSeason
        fields = ('person', 'year', 'role', 'team', 'season', 'story')
        widgets = {
            'season': ModelSelect2Bootstrap(url='autocomplete-seasons',
                                            forward=['year']),
            'team': ModelSelect2Bootstrap(url='autocomplete-teams',
                                          forward=['year'])
        }


class PersonSeasonInRosterForm(PersonSeasonForm):
    """To create PersonSeason from TeamSeasonUpdate."""
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields["team"].disabled = True
        self.fields["season"].disabled = True
        self.fields["year"].disabled = True


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


class ImportForm(forms.Form):
    input = forms.CharField(
        strip=False,
        widget=forms.Textarea(attrs={'cols': 80, 'rows': 20})
    )

    def clean(self):
        data = super(ImportForm, self).clean()
        parse_teams(data['input'])


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
        super().__init__(*args, **kwargs)

    def clean(self):
        data = super(ImportRosterForm, self).clean()
        if data.get("input"):
            parse_rosters(self.request, data)
        # parse_alphabet(self.request, data)
