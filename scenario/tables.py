import django_tables2 as tables
from core.models import ScenarioInfo, Scenario, BaseScenario
from django.utils.html import format_html
import json


class ScenarioInfoTable(tables.Table):
    class Meta:
        model = ScenarioInfo
        template_name = 'django_tables2/bootstrap5.html'
        fields = ('name', 'description', )
        order_by = ('name', 'description', )
        empty_text = 'No data available in table'
        attrs = {
            'class': 'table table-striped'
        }
        search_placeholder = 'Search ...'

class ScenarioTable(tables.Table):
    name = tables.Column(orderable=True)
    counties = tables.Column(orderable=False, empty_values=(), verbose_name='Counties')
    actions = tables.Column(orderable=False, empty_values=())

    def render_name(self, record):
        return format_html('<a href="/scenario/view/{id}/">{name}</a>', id=record.id, name=record.name)

    def render_actions(self, value, record):
        edit_icon = '<i class="material-icons" title="Edit Scenario">add_task</i>'
        execute_icon = '<i class="material-icons" title="Results">fact_check</i>'
        # decision_making_icon = '<i class="material-icons" title="Decision Making">analytics</i>'
        # share_icon = '<i class="material-icons" title="Share Scenario">share</i>'

        if record.base_scenario.status == 'C':
            # Links are clickable and green
            edit_link = '<a href="/step_2/{}/" style="color: green;">{}</a>'.format(record.id, edit_icon)
            execute_link = '<a href="/execution/list/{}/" style="color: green;">{}</a>'.format(record.id, execute_icon)
            # decision_making_link = '<a href="/decision_making/{}" style="margin-left: 10px; color: green;">{}</a>'.format(record.id, decision_making_icon)
            # share_link= '<a href="/scenario/share/{}/" style="margin-left: 10px; color: green;">{}</a>'.format(record.id, share_icon)
        else:
            # Links are not clickable and red
            edit_link = '<span style="color: red;">{}</span>'.format(edit_icon)
            execute_link = '<span style="color: red;">{}</span>'.format(execute_icon)
            # decision_making_link = '<span style="margin-left: 10px; color: red;">{}</span>'.format(decision_making_icon)
            # share_link = '<span style="margin-left: 10px; color: red;">{}</span>'.format(share_icon)

        # return format_html('<div class="action-icons-container">{} {} {} {}</div>'.format(edit_link, execute_link, decision_making_link, share_link))
        return format_html('<div class="action-icons-container">{} {} {} {}</div>'.format(edit_link, execute_link, "", ""))
    
    def render_counties(self, record):
        # Assuming 'geographic_areas_by_state' is a JSON field in the 'base_scenario' model
        areas = record.base_scenario.geographic_areas.all()
        if areas:
            # Organize areas by state
            areas_by_state = {}
            for area in areas:
                areas_by_state.setdefault(area.state, []).append(area.name)
            
            # Format the output: "State: [Area1, Area2, ...]"
            #formatted_areas = [f"{state}: [{', '.join(names)}]" for state, names in areas_by_state.items()]

            formatted_areas = ["<span style='color: green;'>{}</span>: [{}]".format(state, ', '.join(names)) for state, names in areas_by_state.items()]
            # Join the formatted strings with a semicolon and space for separation
            return format_html("; ".join(formatted_areas))
        return "N/A"
    
    class Meta:
        model = Scenario 
        template_name = 'django_tables2/bootstrap5.html'
        # fields = ('id', 'name', 'base_scenario.scenario_info', 'counties', 'updated_at', 'status', 'actions')
        # Removing status till it is fixed
        fields = ('id', 'name', 'base_scenario.scenario_info', 'counties', 'updated_at', 'actions')
        order_by = ('-updated_at', 'name' )
        #empty_text = 'No data available in table'
        attrs = {
            'class': 'my-table table table-striped',
            'th': {
                'class': 'table-heading'
            }
        }
        search_placeholder = 'Search ...'


class BaseScenarioTable(tables.Table):
    class Meta:
        model = BaseScenario
        # Add fields you want to display in your table
        fields = ('scenario_info', 'geographic_areas', 'data',)
        # Additional properties like sequence, orderable can be set here

