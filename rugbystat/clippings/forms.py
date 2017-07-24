from django import forms
from django.contrib.admin.helpers import ActionForm

from .models import Source


class SourceForm(ActionForm):
    source = forms.ModelChoiceField(queryset=Source.objects.all(),
                                    required=False)
