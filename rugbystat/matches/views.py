from dal import autocomplete
from django.db.models import Q
from django.shortcuts import render

from .models import Season


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
