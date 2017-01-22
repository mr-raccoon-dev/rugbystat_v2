from django import forms
from django.db.models import Count

from clippings.models import Document


def get_choices():
    docs_qs = Document.objects.not_deleted().values(
        'year').annotate(count=Count('year')).values_list(
        'year', 'count', ).order_by('year')
    return tuple((doc[0], "{} ({})".format(doc[0], doc[1])) for doc in docs_qs)

class ClippingsForm(forms.Form):
    year = forms.DateField(
        widget=forms.Select(
            choices=get_choices(), attrs={
            'class': 'form-control'
            },
        )
    )
