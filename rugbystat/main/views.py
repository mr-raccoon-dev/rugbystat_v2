from django.shortcuts import render

from teams.forms import PersonForm

from .forms import ClippingsForm


def main_view(request):
    return render(request, 'base.html')


def teams_view(request):
    return render(request, 'teams.html')


def tournaments_view(request):
    return render(request, 'base.html')


def persons_view(request):
    form = PersonForm()
    return render(request, 'persons.html', {'form': form})


def clippings_view(request):
    form = ClippingsForm()
    return render(request, 'documents.html', {'form': form})
