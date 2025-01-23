from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from core.models import ScenarioInfo, Scenario, Execution

# Create your views here.

class ScenarioInfoView(LoginRequiredMixin, TemplateView):
    template_name = 'step_1/info.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scenario_id = self.kwargs.get('id')  # Assuming you're passing the ID in the URL

        scenario = Scenario.objects.get(pk=scenario_id)

        bmps = scenario.bmps

        manure_transport_bmps = False

        if 'target_items' in bmps.keys() and 'Manure Transport' in bmps['target_items'].keys():
            manure_transport_bmps = True

        counties = scenario.base_scenario.geographic_areas.all()
        counties_list = [county.name for county in counties]

        context['scenario_info'] = scenario.base_scenario.scenario_info 
        context['counties'] = counties_list 
        context['scenario_id'] = scenario_id
        context['manure_transport_bmps'] = manure_transport_bmps

               
        return context
    
class ScenarioInfoExecView(LoginRequiredMixin, TemplateView):
    template_name = 'step_1/info_exec.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        execution_id = self.kwargs.get('id')  # Assuming you're passing the ID in the URL

        execution = Execution.objects.get(pk=execution_id)

        bmps = execution.bmps

        manure_transport_bmps = False

        if 'target_items' in bmps.keys() and 'Manure Transport' in bmps['target_items'].keys():
            manure_transport_bmps = True

        counties = execution.scenario.base_scenario.geographic_areas.all()
        counties_list = [county.name for county in counties]

        context['scenario_info'] = execution.scenario.base_scenario.scenario_info 
        context['counties'] = counties_list 
        context['execution_id'] = execution_id
        context['manure_transport_bmps'] = manure_transport_bmps

               
        return context
