from django import forms
from clippings.models import Document


class ClippingsForm(forms.Form):
    year = forms.DateField(
        widget=forms.Select(
            choices=tuple(Document.objects.not_deleted().values_list(
                'year', 'year').order_by('year').distinct()
            ), attrs={
            'class': 'form-control'
            },
        )
    )
