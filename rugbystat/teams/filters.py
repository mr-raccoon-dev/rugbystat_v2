import operator
from functools import reduce

from django.db import models
from django.utils import six
from rest_framework.compat import distinct
from rest_framework.filters import SearchFilter

__author__ = 'krnr'


class TeamFullTextFilter(SearchFilter):
    search_param = 'fulltext'
    search_fields = ('$story', )

    def filter_queryset(self, request, queryset, view):
        search_fields = self.search_fields
        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms:
            return queryset

        orm_lookups = [
            self.construct_search(six.text_type(search_field))
            for search_field in search_fields
        ]

        base = queryset
        for search_term in search_terms:
            queries = [
                models.Q(**{orm_lookup: search_term})
                for orm_lookup in orm_lookups
            ]
            queryset = queryset.filter(reduce(operator.or_, queries))

        if self.must_call_distinct(queryset, search_fields):
            # Filtering against a many-to-many field requires us to
            # call queryset.distinct() in order to avoid duplicate items
            # in the resulting queryset.
            # We try to avoid this if possible, for performance reasons.
            queryset = distinct(queryset, base)
        return queryset
