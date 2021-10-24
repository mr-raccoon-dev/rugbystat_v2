import django_filters

from .models import Season

class SeasonFilter(django_filters.FilterSet):
    year = django_filters.NumberFilter(field_name='date_end', lookup_expr='year')

    class Meta:
        model = Season
        fields = ['year', 'tourn_id']

