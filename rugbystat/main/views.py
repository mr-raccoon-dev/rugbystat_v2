from collections import Counter

from django.shortcuts import render

from clippings.models import Document
from teams.forms import PersonForm

from .forms import ClippingsForm


def main_view(request):
    return render(request, 'base.html')


def teams_view(request):
    return render(request, 'teams.html')


def persons_view(request):
    form = PersonForm()
    return render(request, 'persons.html', {'form': form})


def clippings_view(request):
    form = ClippingsForm()
    # TODO: rewrite for one query
    qs = Document.objects.values_list('source__kind', flat=True)
    counter = Counter(qs)
    total = sum(counter.values())
    return render(request, 'documents.html', {'form': form,
                                              'total': counter,
                                              'sum_total': total})
