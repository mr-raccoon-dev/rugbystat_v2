from django.shortcuts import render

from .forms import ClippingsForm


def main_view(request):
    return render(request, 'base.html')


def teams_view(request):
    return render(request, 'teams.html')


def tournaments_view(request):
    return render(request, 'base.html')


def persons_view(request):
    return render(request, 'persons.html')


def clippings_view(request):
    form = ClippingsForm()
    return render(request, 'documents.html', {'form': form})
