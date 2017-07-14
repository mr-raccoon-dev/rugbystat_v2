from rest_framework import viewsets, filters

from .filters import TeamFullTextFilter
from .models import Team, Person, PersonSeason
from .serializers import (TeamSerializer, 
                          PersonSerializer, PersonSeasonSerializer)

__author__ = 'krnr'


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Team.objects.select_related(
        'city', 'parent').prefetch_related('document_set').order_by(
        'year', 'id')
    serializer_class = TeamSerializer
    filter_backends = (TeamFullTextFilter,
                       filters.SearchFilter,
                       filters.DjangoFilterBackend,)
    search_fields = ('^short_name',)
    filter_fields = ('year', 'short_name',)
    page_size_query_param = 'limit'


class PersonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


class PersonSeasonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PersonSeason.objects.all()
    serializer_class = PersonSeasonSerializer
