from django_filters import CharFilter
from django_filters.rest_framework import FilterSet

from clippings.models import SourceObject

__author__ = 'krnr'


class ClippingsFilter(FilterSet):
    pass


class SourceObjectFilter(FilterSet):
    type = CharFilter(name="source__type")
    title = CharFilter(name="source__title")

    class Meta:
        model = SourceObject
        fields = ['year', 'date', 'type', 'title']
