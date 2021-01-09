from rest_framework import viewsets, mixins

from .models import Match, Season
from .serializers import MatchSerializer, SeasonSerializer


class MatchViewSet(mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   viewsets.ReadOnlyModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer


class SeasonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer

