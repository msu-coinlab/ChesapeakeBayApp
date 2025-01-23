

import django_tables2 as tables
from django.utils.formats import number_format




class BmpConstraintCustomDataTable(tables.Table):
    name = tables.Column(orderable=True)  # Assuming you want to sort by name
    max_quantity = tables.Column(orderable=True, attrs={"td": {"style": "text-align: right;"},
                                                         "th": {"style": "text-align: right;"}})
    def render_max_quantity(self, value):
        return number_format(value, 2)
        #return "$ {:,.2f}".format(value)

    class Meta:
        template_name = 'django_tables2/bootstrap.html'
        order_by = 'name'  # Default sorting

    # Custom sorting logic (if needed)
    def order_max_quantity(self, queryset, is_descending):
        queryset = queryset.order_by(('-' if is_descending else '') + 'max_quantity')
        return (queryset, True)

