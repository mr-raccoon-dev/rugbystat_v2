from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import DetailView

from .forms import ImportForm
from .models import Person


def import_teams(request):
    if request.method == 'POST':
        form = ImportForm(request.POST)
        if form.is_valid():
            return HttpResponse('OK', content_type="text/plain")
        else:
            return HttpResponse('False', content_type="text/plain")
    else:
        form = ImportForm()
    return render(request, 'import.html', {'form': form})


class PersonDetailView(DetailView):
    model = Person
