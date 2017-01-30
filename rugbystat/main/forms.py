from django import forms
from django.db.models import Count

from clippings.models import Document, Source


def get_years():
    docs_qs = Document.objects.not_deleted().values(
        'year').annotate(count=Count('year')).values_list(
        'year', 'count', ).order_by('year')
    return tuple(
        [('', '---')] + 
        [(doc[0], "{} (всего {})".format(doc[0], doc[1])) 
        for doc in docs_qs]
    )

def get_sources():
    return tuple(
        [('', '---')] + 
        [(source.id, source) 
        for source in Source.objects.exclude(scans__isnull=True)]
    )


class ClippingsForm(forms.Form):
    year = forms.DateField(
        widget=forms.Select(
            choices=get_years(), 
            attrs={'class': 'form-control'},
        )
    )
    source = forms.ChoiceField(
        choices=get_sources(),
        widget=forms.Select(attrs={'class': 'form-control'},)
    )
    source_type = forms.ChoiceField(
        choices=tuple([('', '---')] + list(Source.TYPE_CHOICES)), 
        widget=forms.Select(attrs={'class': 'form-control'},)
    )
