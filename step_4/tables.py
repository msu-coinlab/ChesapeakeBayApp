
import django_tables2 as tables
from core.models import BmpCostCustom

from django.utils.formats import number_format



class BmpCostCustomTable(tables.Table):
    '''
    delete = tables.TemplateColumn(
        template_name='step_4/delete_column_template.html',
        orderable=False,
        exclude_from_export=True,
        verbose_name=''
    )
    '''

    class Meta:
        model = BmpCostCustom
        template_name = 'django_tables2/bootstrap.html'
        fields = ('bmp_cost__state_name', 'bmp_cost__bmp__name', 'original_cost', 'new_cost')  # Add or remove fields as needed


class BmpCostCustomDataTable(tables.Table):
    state = tables.Column(orderable=True)  # Assuming you want to sort by name
    name = tables.Column(orderable=True)  # Assuming you want to sort by name
    original_cost = tables.Column(orderable=True, attrs={"td": {"style": "text-align: right;"},
                                                         "th": {"style": "text-align: right;"}})
    new_cost = tables.Column(orderable=True, attrs={"td": {"style": "text-align: right;"},
                                                    "th": {"style": "text-align: right;"}})

    def render_original_cost(self, value):
        return number_format(value, 2)
        #return "$ {:,.2f}".format(value)

    def render_new_cost(self, value):
        return number_format(value, 2)

    class Meta:
        template_name = 'django_tables2/bootstrap.html'
        order_by = 'name'  # Default sorting

    # Custom sorting logic (if needed)
    def order_original_cost(self, queryset, is_descending):
        queryset = queryset.order_by(('-' if is_descending else '') + 'original_cost')
        return (queryset, True)

    def order_new_cost(self, queryset, is_descending):
        queryset = queryset.order_by(('-' if is_descending else '') + 'new_cost')
        return (queryset, True)
