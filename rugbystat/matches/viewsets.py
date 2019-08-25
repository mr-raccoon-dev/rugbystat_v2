from rest_framework import viewsets, mixins

from .models import Match
from .serializers import MatchSerializer


class MatchViewSet(mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   viewsets.ReadOnlyModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
