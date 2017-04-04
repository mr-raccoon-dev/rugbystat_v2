from django_filters import CharFilter
from django_filters.rest_framework import FilterSet

from clippings.models import SourceObject

__author__ = 'krnr'


class SourceObjectFilter(FilterSet):
    kind = CharFilter(name="source__kind")
    title = CharFilter(name="source__title")

    class Meta:
        model = SourceObject
        fields = ['year', 'date', 'kind', 'title']
