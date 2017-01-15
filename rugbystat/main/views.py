from django.shortcuts import render


def main_view(request):
    return render(request, 'base.html')


def teams_view(request):
    return render(request, 'teams.html')


def tournaments_view(request):
    return render(request, 'base.html')


def persons_view(request):
    return render(request, 'base.html')


def clippings_view(request):
    return render(request, 'base.html')

