import django_tables2 as tables
from django_tables2.paginators import Paginator
import locale
from django.utils.html import format_html

class SolutionCustomDataTable(tables.Table):
    id = tables.Column(visible=False)  # Assuming you want to sort by name
    num = tables.Column(orderable=False, verbose_name='#')  # Assuming you want to sort by name
    Cost = tables.Column(orderable=False , verbose_name='Cost ($)')  # Assuming you want to sort by name
    N = tables.Column(orderable=False, verbose_name='Nitrogen (lbs/yr)')  # Assuming you want to sort by name
    P = tables.Column(orderable=False, verbose_name='Phosphorus (lbs/yr)')  # Assuming you want to sort by name
    S = tables.Column(orderable=False, verbose_name='Sediments (lbs/yr)')  # Assuming you want to sort by name
    actions = tables.Column(orderable=False, empty_values=())

    def render_actions(self, value, record):
        dashboard_icon= '<i class="material-icons">dashboard</i>'
        insights_icon= '<i class="material-icons">insights</i>'
        duplicate_icon = '<i class="material-icons">content_copy</i>'
        download_icon = '<i class="material-icons">file_download</i>'
        delete_icon = '<i class="material-icons">delete</i>'


        loads_by_sector_link = '<a href="/solution/view_by_sector/{}/" title="View results" style="margin-left: 10px; color: green;">{}</a>'.format(record['id'], insights_icon)

        results_link = '<a href="/solution/view/{}/" title="View BMPs" style="margin-left: 10px; color: green;">{}</a>'.format(record['id'], dashboard_icon)
        duplicate_link = '<a href="/solution/duplicate/{}/" title="Duplicate and edit solution" style="margin-left: 10px; color: green;">{}</a>'.format(record['id'], duplicate_icon)
        download_link = '<a href="/solution/download/{}/" title="Download solution" style="margin-left: 10px; color: green;">{}</a>'.format(record['id'], download_icon)
        delete_link = '<a href="/solution/duplicate/{}/" title="Delete solution" style="margin-left: 10px; color: red;">{}</a>'.format(record['id'], delete_icon)

        return format_html('{} {} {} {} {}'.format(loads_by_sector_link, results_link, duplicate_link, download_link, delete_link))

    def render_Cost(self, value):
        return locale.format_string("%d", value, grouping=True) if value else ''  # Format with commas as thousands separator
    def render_N(self, value):
        return locale.format_string("%d", value, grouping=True) if value else ''  # Format with commas as thousands separator
    def render_P(self, value):
        return locale.format_string("%d", value, grouping=True) if value else ''  # Format with commas as thousands separator
    def render_S(self, value):
        return locale.format_string("%d", value, grouping=True) if value else ''  # Format with commas as thousands separator

    class Meta:
        template_name = 'django_tables2/bootstrap-responsive.html'
        attrs = {'class': 'my-table table table-striped table-bordered', 'style': 'width:100%;'}
        order_by = 'id'  # Default sorting


class SolutionBySectorTable(tables.Table):
    id = tables.Column(orderable=True)  # Assuming you want to sort by name
    sector = tables.Column(orderable=False, verbose_name='Sector')  # Assuming you want to sort by name
    N = tables.Column(orderable=False, verbose_name='Nitrogen (lbs/yr)')  # Assuming you want to sort by name
    P = tables.Column(orderable=False, verbose_name='Phosphorus (lbs/yr)')  # Assuming you want to sort by name
    S = tables.Column(orderable=False, verbose_name='Sediments (lbs/yr)')  # Assuming you want to sort by name
    actions = tables.Column(orderable=False, empty_values=())

    def render_actions(self, value, record):
        results_icon = '<i class="material-icons">poll</i>'

        results_link = '<a href="/solution/view/{}/" style="margin-left: 10px; color: green;">{}</a>'.format(record['id'], results_icon)

        return format_html('{}'.format(results_link))

    def render_N(self, value):
        return locale.format_string("%d", value, grouping=True) if value else 0  # Format with commas as thousands separator
    def render_P(self, value):
        return locale.format_string("%d", value, grouping=True) if value else 0  # Format with commas as thousands separator
    def render_S(self, value):
        return locale.format_string("%d", value, grouping=True) if value else 0  # Format with commas as thousands separator


    class Meta:
        template_name = 'django_tables2/bootstrap-responsive.html'
        attrs = {'class': 'my-table table table-striped table-bordered', 'style': 'width:100%;'}
        order_by = 'id'  # Default sorting


class SolutionBySectorTableSimple(tables.Table):
    id = tables.Column(orderable=True, visible=False)  # Assuming you want to sort by name
    sector = tables.Column(orderable=True, verbose_name='Sector')  # Assuming you want to sort by name
    N = tables.Column(orderable=True, verbose_name='Nitrogen (lbs/yr)')  # Assuming you want to sort by name
    P = tables.Column(orderable=True, verbose_name='Phosphorus (lbs/yr)')  # Assuming you want to sort by name
    S = tables.Column(orderable=True, verbose_name='Sediments (lbs/yr)')  # Assuming you want to sort by name

    def render_N(self, value):
        return locale.format_string("%d", value, grouping=True) if value else 0  # Format with commas as thousands separator
    def render_P(self, value):
        return locale.format_string("%d", value, grouping=True) if value else 0  # Format with commas as thousands separator
    def render_S(self, value):
        return locale.format_string("%d", value, grouping=True) if value else 0  # Format with commas as thousands separator


    class Meta:
        template_name = 'django_tables2/bootstrap-responsive.html'
        attrs = {'class': 'my-table2 table table-striped table-bordered', 'style': 'width:100%;'}


class SolutionBySectorTableSimple2(tables.Table):
    county = tables.Column(orderable=True, verbose_name='County')
    state = tables.Column(orderable=True, verbose_name='State')
    lrs= tables.Column(orderable=True, verbose_name='lrs')
    sector = tables.Column(orderable=True, verbose_name='Sector')
    N = tables.Column(orderable=True, verbose_name='Nitrogen (lbs/yr)')
    P = tables.Column(orderable=True, verbose_name='Phosphorus (lbs/yr)')
    S = tables.Column(orderable=True, verbose_name='Sediments (lbs/yr)')

    def __init__(self, *args, **kwargs):
        self.totals = kwargs.pop('totals', {})
        super(SolutionBySectorTableSimple2, self).__init__(*args, **kwargs)

    class Meta:
        template_name = 'solution/partials/_sediments_table_with_foot.html'  # Point to your custom template
        attrs = {'class': 'my-table2 table table-striped table-bordered', 'style': 'width:100%;'}

class EfficiencyBmpCustomDataTable(tables.Table):

    #id = tables.Column(orderable=True)  # Assuming you want to sort by name
    state_id = tables.Column(visible=False)  # Assuming you want to sort by name
    county_id = tables.Column(visible=False)  # Assuming you want to sort by name
    lrs_id = tables.Column(visible=False)  # Assuming you want to sort by name
    lrs = tables.Column(orderable=True)  # Assuming you want to sort by name
    agency = tables.Column(orderable=True)  # Assuming you want to sort by name
    load_src = tables.Column(orderable=True)  # Assuming you want to sort by name
    sector = tables.Column(orderable=True)  # Assuming you want to sort by name
    bmp= tables.Column(orderable=True)  # Assuming you want to sort by name
    acres = tables.Column(orderable=True)  # Assuming you want to sort by name
    cost = tables.Column(orderable=True)  # assuming you want to sort by name
    #actions = tables.Column(orderable=False, empty_values=())

    #def render_actions(self, value, record):
    #    results_icon = '<i class="material-icons">poll</i>'

    #    results_link = '<a href="/solution/list/{}/" style="margin-left: 10px; color: green;">{}</a>'.format(record['id'], results_icon)

    #    return format_html('{}'.format(results_link))

    def render_acres(self, value):   
        return locale.format_string("%.2f", value, grouping=True) if value else ''  # Format with commas as thousands separator
    def render_cost(self, value):   
        return locale.format_string("%.2f", value, grouping=True) if value else ''  # Format with commas as thousands separator
    class Meta:
        template_name = 'django_tables2/bootstrap-responsive.html'
        attrs = {'class': 'my-table-efficiency table table-striped table-bordered', 'style': 'width:100%;'}
        order_by = 'id'  # Default sorting
    per_page = 20
    paginator_class = Paginator

class LoadsTable(tables.Table):

    state = tables.Column(orderable=True)  # Assuming you want to sort by name
    county = tables.Column(orderable=True)  # Assuming you want to sort by name
    lrs = tables.Column(orderable=True)  # Assuming you want to sort by name
    sector = tables.Column(orderable=True)  # Assuming you want to sort by name
    Ns = tables.Column(orderable=True, verbose_name='Nitrogen (lbs/yr)')  # Assuming you want to sort by name
    Ps= tables.Column(orderable=True, verbose_name='Phosphorus (lbs/yr)')  # Assuming you want to sort by name
    Ss= tables.Column(orderable=True, verbose_name='Sediments (lbs/yr)')  # Assuming you want to sort by name

    class Meta:
        template_name = 'django_tables2/bootstrap-responsive.html'
        attrs = {'class': 'my-table-loads table table-striped table-bordered', 'style': 'width:100%;'}

        order_by = 'state'  # Default sorting
    per_page = 20
    paginator_class = Paginator
class SummaryEfficiencyBmpCustomDataTable(tables.Table):

    #id = tables.Column(orderable=True)  # Assuming you want to sort by name
    #county = tables.Column(orderable=True)  # Assuming you want to sort by name
    bmp= tables.Column(orderable=True)  # Assuming you want to sort by name
    amount = tables.Column(orderable=True)  # Assuming you want to sort by name


    def render_amount(self, value):   
        return locale.format_string("%.2f", value, grouping=True) if value else ''  # Format with commas as thousands separator
    class Meta:
        template_name = 'django_tables2/bootstrap-responsive.html'
        attrs = {'class': 'my-table-summary-efficiency table table-striped table-bordered', 'style': 'width:100%;'}
        order_by = 'id'  # Default sorting
    paginator_class = Paginator

class EfficiencyBmpCustomDataTable2(tables.Table):

    id = tables.Column(orderable=True)  # Assuming you want to sort by name
    lrs = tables.Column(orderable=True)  # Assuming you want to sort by name
    agency = tables.Column(orderable=True)  # Assuming you want to sort by name
    load_src = tables.Column(orderable=True)  # Assuming you want to sort by name
    sector = tables.Column(orderable=True)  # Assuming you want to sort by name
    bmp= tables.Column(orderable=True)  # Assuming you want to sort by name
    amount = tables.Column(orderable=True)  # Assuming you want to sort by name
    actions = tables.Column(orderable=False, empty_values=())

    def render_actions(self, value, record):
        edit_icon = '<i class="material-icons">edit</i>'
        delete_icon = '<i class="material-icons">delete</i>'

        edit_link = '<a href="/solution/list/{}/" style="margin-left: 10px; color: green;">{}</a>'.format(record['id'], edit_icon)
        delete_link = '<a href="/solution/list/{}/" style="margin-left: 10px; color: red;">{}</a>'.format(record['id'], delete_icon)

        return format_html('{} {}'.format(edit_link, delete_link))

    def render_amount(self, value):   
        return locale.format_string("%.2f", value, grouping=True) if value else ''  # Format with commas as thousands separator
    class Meta:
        template_name = 'django_tables2/bootstrap-responsive.html'
        attrs = {'class': 'my-table-efficiency table table-striped table-bordered', 'style': 'width:100%;'}
        order_by = 'id'  # Default sorting
    per_page = 20
    paginator_class = Paginator




class AnimalBmpCustomDataTable2(tables.Table):

    id = tables.Column(orderable=True)  # Assuming you want to sort by name
    base_condition = tables.Column(orderable=True)  # Assuming you want to sort by name

    county = tables.Column(orderable=True)  # Assuming you want to sort by name
    load_src = tables.Column(orderable=True)  # Assuming you want to sort by name
    sector = tables.Column(orderable=True)  # Assuming you want to sort by name
    animal = tables.Column(orderable=True)  # Assuming you want to sort by name
    bmp = tables.Column(orderable=True)  # Assuming you want to sort by name
    amount = tables.Column(orderable=True)  # Assuming you want to sort by name
    actions = tables.Column(orderable=False, empty_values=())

    def render_actions(self, value, record):
        edit_icon = '<i class="material-icons">edit</i>'
        delete_icon = '<i class="material-icons">delete</i>'

        edit_link = '<a href="/solution/list/{}/" style="margin-left: 10px; color: green;">{}</a>'.format(record['id'], edit_icon)
        delete_link = '<a href="/solution/list/{}/" style="margin-left: 10px; color: red;">{}</a>'.format(record['id'], delete_icon)

        return format_html('{} {}'.format(edit_link, delete_link))

    def render_amount(self, value):   
        return locale.format_string("%.2f", value, grouping=True) if value else ''  # Format with commas as thousands separator

    class Meta:
        template_name = 'django_tables2/bootstrap-responsive.html'
        attrs = {'class': 'my-table-animal table table-striped table-bordered', 'style': 'width:100%;'}
        order_by = 'id'  # Default sorting
    per_page = 20

class AnimalBmpCustomDataTable(tables.Table):

    id = tables.Column(orderable=True)  # Assuming you want to sort by name

    county_id = tables.Column(visible=False)  # Assuming you want to sort by name
    base_condition = tables.Column(orderable=True)  # Assuming you want to sort by name
    state = tables.Column(orderable=True)  # Assuming you want to sort by name
    county = tables.Column(orderable=True)  # Assuming you want to sort by name
    load_src = tables.Column(orderable=True)  # Assuming you want to sort by name
    sector = tables.Column(orderable=True)  # Assuming you want to sort by name
    animal = tables.Column(orderable=True)  # Assuming you want to sort by name
    bmp = tables.Column(orderable=True)  # Assuming you want to sort by name
    amount = tables.Column(orderable=True)  # Assuming you want to sort by name
    cost = tables.Column(orderable=True)  # Assuming you want to sort by name

    def render_amount(self, value):   
        return locale.format_string("%.2f", value, grouping=True) if value else ''  # Format with commas as thousands separator

    def render_cost(self, value):   
        return locale.format_string("%.2f", value, grouping=True) if value else ''  # Format with commas as thousands separator
    class Meta:
        template_name = 'django_tables2/bootstrap-responsive.html'
        attrs = {'class': 'my-table-animal table table-striped table-bordered', 'style': 'width:100%;'}
        order_by = 'id'  # Default sorting
    per_page = 20

class ManureBmpCustomDataTable(tables.Table):

    id = tables.Column(orderable=True)  # Assuming you want to sort by name
    county_from = tables.Column(orderable=True)  # Assuming you want to sort by name
    county_to = tables.Column(orderable=True)  # Assuming you want to sort by name
    load_src = tables.Column(orderable=True)  # Assuming you want to sort by name
    sector = tables.Column(orderable=True)  # Assuming you want to sort by name
    animal = tables.Column(orderable=True)  # Assuming you want to sort by name
    bmp = tables.Column(orderable=True)  # Assuming you want to sort by name
    amount = tables.Column(orderable=True)  # Assuming you want to sort by name
    actions = tables.Column(orderable=False, empty_values=())

    def render_actions(self, value, record):
        results_icon = '<i class="material-icons">poll</i>'

        results_link = '<a href="/solution/list/{}/" style="margin-left: 10px; color: green;">{}</a>'.format(record['id'], results_icon)

        return format_html('{}'.format(results_link))

    def render_amount(self, value):   
        return locale.format_string("%.2f", value, grouping=True) if value else ''  # Format with commas as thousands separator
    class Meta:
        template_name = 'django_tables2/bootstrap-responsive.html'
        attrs = {'class': 'my-table-manure table table-striped table-bordered', 'style': 'width:100%;'}
        order_by = 'id'  # Default sorting
    per_page = 20
    paginator_class = Paginator

locale.setlocale(locale.LC_ALL, '')
