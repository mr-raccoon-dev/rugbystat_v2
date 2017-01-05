from rest_framework import viewsets, filters
from clippings.filters import SourceObjectFilter

from .models import Document, Source, SourceObject
from .serializers import (DocumentSerializer,
                          SourceSerializer,
                          SourceObjectSerializer,
                          )

__author__ = 'krnr'


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    filter_fields = ('year', 'date', 'is_image')


class SourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend)
    search_fields = ('^title', )
    filter_fields = ('title', 'type')


class SourceObjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SourceObject.objects.all()
    serializer_class = SourceObjectSerializer
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend)
    filter_class = SourceObjectFilter
    search_fields = ('^source__title', '^edition')
    # filter_fields = ('year', 'date',)
