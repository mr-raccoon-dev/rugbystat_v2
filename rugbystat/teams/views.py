from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import UpdateView

from .forms import ImportForm, PersonForm, PersonSeasonForm, TeamForm
from .models import Person, Team


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


class TeamUpdateView(UpdateView):
    model = Team
    form_class = TeamForm


class PersonUpdateView(UpdateView):
    model = Person
    form_class = PersonForm

    def get_context_data(self, **kwargs):
        kwargs = super(PersonUpdateView, self).get_context_data(**kwargs)
        form = PersonSeasonForm(initial={'person': self.object.pk})
        kwargs['season_form'] = form
        return kwargs
