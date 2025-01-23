import django_filters
from core.models import Execution

class ExecutionFilter(django_filters.FilterSet):
    scenario_id = django_filters.UUIDFilter(field_name='scenario__id')

    class Meta:
        model = Execution
        fields = ['scenario_id']
