from datetime import date

from django.contrib.admin.filters import (AllValuesFieldListFilter, 
                                          SimpleListFilter)
from django.db.models.functions import ExtractYear
from django.utils.translation import ugettext_lazy as _


class DropdownFilter(AllValuesFieldListFilter):
    template = 'admin/dropdown_filter.html'

    def __init__(self, *args, **kwargs):
        super(DropdownFilter, self).__init__(*args, **kwargs)
        self.lookup_choices = [None] + list(self.lookup_choices)


class DateEndListFilter(SimpleListFilter):
    title = _('Year')

    # which field is used to extract year
    model_field = 'date_end'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        values =  sorted(list(set(
            model_admin.model.objects.annotate(
                year=ExtractYear(self.model_field)
            ).values_list('year', flat=True)
        )))

        return (
            (value, value) for value in values
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            year = int(self.value())
            return queryset.filter(date_end__gte=date(year, 1, 1),
                                   date_end__lte=date(year, 12, 31))
