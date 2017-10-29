from collections import Counter

from django.db.models import Count
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
    qs = Document.objects.values_list('source__kind', flat=True)
    # qs = dict(
    #     Document.objects.values_list('source__kind')
    #     .annotate(Count('id')).order_by()
    # )
    counter = Counter(qs)
    total = sum(counter.values())
    null = counter[None]
    return render(request, 'documents.html', {'form': form,
                                              'total': counter,
                                              'null': null,
                                              'sum_total': total})
