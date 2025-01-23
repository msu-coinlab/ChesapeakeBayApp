
import django_tables2 as tables
from django.utils.html import format_html


class ExecutionCustomDataTable(tables.Table):
    id = tables.Column(visible=True)  # Assuming you want to sort by name
    execution = tables.Column(orderable=True, verbose_name="# Optimization Run")  # Assuming you want to sort by name
    solutions = tables.Column(orderable=True, verbose_name="# Solutions")  # Assuming you want to sort by name
    #avg_Cost = tables.Column(orderable=True)  # Assuming you want to sort by name
    #avg_N = tables.Column(orderable=True, verbose_name='Avg Nitrogen (lbs/yr)')  # Assuming you want to sort by name
    #avg_P = tables.Column(orderable=True, verbose_name='Avg Phosphorus (lbs/yr)')  # Assuming you want to sort by name
    #avg_S = tables.Column(orderable=True, verbose_name='Avg Sediments (lbs/yr)')  # Assuming you want to sort by name
    actions = tables.Column(orderable=False, empty_values=())


    def render_actions(self, value, record):
        settings_icon = '<i class="material-icons">display_settings</i>'
        layers_icon = '<i class="material-icons">layers</i>'
        delete_icon = '<i class="material-icons">delete</i>'
        share_icon = '<i class="material-icons">share</i>'

        settings_link = '<a href="/step_1/by-exec/{}/" style="margin-left: 10px; color: green;">{}</a>'.format(record['id'], settings_icon)
        layers_link = '<a href="/solution/list/{}/" style="margin-left: 10px; color: green;">{}</a>'.format(record['id'], layers_icon)
        delete_link = '<a href="/solution/plot/{}/" style="margin-left: 10px; color: red;">{}</a>'.format(record['id'], delete_icon)
        share_link = '<a href="/solution/share/{}/" style="margin-left: 10px; color: green;">{}</a>'.format(record['id'], share_icon)

        return format_html('{} {} {} {}'.format(settings_link, layers_link, share_link, delete_link))

    class Meta:
        template_name = 'django_tables2/bootstrap-responsive.html'
        attrs = {'class': 'my-table table table-striped table-bordered', 'style': 'width:100%;'}
        order_by = 'id'  # Default sorting

