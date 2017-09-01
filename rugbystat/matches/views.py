from datetime import datetime

from dal import autocomplete
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from .forms import ImportForm, SeasonForm
from .models import Tournament, Season


class TournamentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # if not self.request.user.is_authenticated():
        #     return Season.objects.none()

        qs = Tournament.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        
        return qs


class SeasonAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # if not self.request.user.is_authenticated():
        #     return Season.objects.none()

        qs = Season.objects.all()

        year = self.forwarded.get('year', None)
        if year:
            qs = qs.filter(Q(date_end__year=year) | 
                           Q(date_start__year=year))
        
        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


def import_seasons(request):
    obj_form = SeasonForm()
    status = None

    if request.method == 'POST':
        form = ImportForm(request.POST, request=request)

        if form.is_valid():
            status = 'OK'
            obj_form = SeasonForm(instance=form.season)
        else:
            status = 'False'
    else:
        form = ImportForm()
    return render(request, 
                  'import.html', 
                  {
                      'form': form, 
                      'status': status,
                      'obj_form': obj_form
                  })
