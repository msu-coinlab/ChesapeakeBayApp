import django_filters
from django_filters import DateFromToRangeFilter
from core.models import ScenarioInfo, Scenario
from bootstrap_datepicker_plus.widgets import DatePickerInput
from core.models import GeographicArea
from django_filters import DateFromToRangeFilter
from django_filters.widgets import DateRangeWidget


class ScenarioInfoFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = ScenarioInfo
        fields = ('name', )

class ScenarioFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    updated_at = DateFromToRangeFilter(
        field_name='updated_at',
        label='Updated at (Between)',
        widget=DateRangeWidget(attrs={'type': 'date'})
    )

    created_at_start = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Created At (Start)',
        widget=DatePickerInput(attrs={'placeholder': 'Select start date'})
    )

    created_at_end = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Created At (End)',
        widget=DatePickerInput(attrs={'placeholder': 'Select end date'})
    )

    geographic_areas = django_filters.ModelChoiceFilter(
        queryset=GeographicArea.objects.all(),  # Replace with your actual queryset
        label='Geographic Areas',
        to_field_name='id',
        required=False  # Set required to False to make it optional
    )

    class Meta:
        model = Scenario
        fields = ('name', 'scenario_info', 'geographic_areas', 'created_at_start', 'created_at_end', 'updated_at')

        #layout = (
        #('name', 'scenario_info'),
        #('created_at_start', 'geographic_areas'),
        #)
