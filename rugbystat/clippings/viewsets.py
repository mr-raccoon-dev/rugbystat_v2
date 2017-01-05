from rest_framework import viewsets, filters
from clippings.filters import SourceObjectFilter

from .models import Document, Source, SourceObject
from .serializers import (DocumentSerializer,
                          SourceSerializer,
                          SourceObjectSerializer,
                          )

__author__ = 'krnr'


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Document.objects.prefetch_related('versions')
    serializer_class = DocumentSerializer
    filter_fields = ('year', 'date', 'is_image')

    def get_queryset(self):
        qs = self.queryset
        team = self.kwargs.get('team_id', None)
        if team:
            qs = qs.filter(tag__team__pk=team)
        return qs


class SourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Source.objects.prefetch_related('instances__scans')
    serializer_class = SourceSerializer
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend)
    search_fields = ('^title', )
    filter_fields = ('title', 'type')


class SourceObjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SourceObject.objects.prefetch_related('scans')
    serializer_class = SourceObjectSerializer
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend)
    filter_class = SourceObjectFilter
    search_fields = ('^source__title', '^edition')
    # filter_fields = ('year', 'date',)
