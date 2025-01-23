from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import ScenarioInfo, Scenario, BaseScenario, State, Execution
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
import json
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.

def sum_scenario_loads(scenario_id):
    try:
        # Fetch the BaseScenario instance
        base_scenario = BaseScenario.objects.get(pk=scenario_id)

        # Parse the JSON data
        data = base_scenario.data

        # Extract the lists
        sum_load_invalid = data.get('sum_load_invalid', [])
        sum_load_valid = data.get('sum_load_valid', [])

        # Ensure the lists are of the same length
        if len(sum_load_invalid) != len(sum_load_valid):
            raise ValueError("Lists 'sum_load_invalid' and 'sum_load_valid' are not of the same length.")

        # Sum up the elements of the same index
        total_loads = [invalid + valid for invalid, valid in zip(sum_load_invalid, sum_load_valid)]
        if len(total_loads) < 4:
            total_loads.append(0.0)

        return total_loads

    except ObjectDoesNotExist:
        # Handle the case where BaseScenario does not exist for the given id
        print("BaseScenario with the provided ID does not exist.")
        return []
    except ValueError as e:
        # Handle the case where the lists are not of the same length
        print(str(e))
        return []


def sum_amount_values(scenario_id):
    try:
        # Fetch the BaseScenario instance
        base_scenario = BaseScenario.objects.get(pk=scenario_id)

        # Extract the data
        data = base_scenario.data

        # Extract the 'amount' dictionary
        amount_dict = data.get('amount', {})

        # Sum up all the values in the 'amount' dictionary
        total_amount = sum(amount_dict.values())

        return total_amount

    except BaseScenario.DoesNotExist:
        # Handle the case where BaseScenario does not exist for the given id
        print("BaseScenario with the provided ID does not exist.")
        return 0


def update_scenario_loads_field(scenario_id, field_name, new_value):
    # Update the field using a dictionary
    scenario = get_object_or_404(Scenario, pk=scenario_id)
    scenario.loads[field_name] = new_value
    scenario.save()

    '''loads = models.JSONField(default=dict, null=True, blank=True)
    update_dict = {field_name: new_value}
    if Scenario.objects.filter(pk=scenario_id).exists():
        Scenario.objects.filter(pk=scenario_id).update(**update_dict)
    '''

@require_POST
def update_scenario_loads(request):
    if request.method == "POST" and request.headers.get('Hx-Request') == 'true':

        new_value_str = request.POST.get('new_value')
        field_name = request.POST.get('field_name')
        scenario_id_str = request.POST.get('scenario_id')
        print(new_value_str)


        scenario_id = 0
        if scenario_id_str is not None:
            try:
                scenario_id = int(scenario_id_str)
            except ValueError:
                # Handle the case where new_acres is not a valid number
                return JsonResponse({'status': 'error', 'message': 'Invalid value for current_acres'})
        else:
            # 'current_acres' not provided
            return JsonResponse({'status': 'error', 'message': 'current_acres not provided'})

        if field_name is not None and new_value_str is not None:
            try:
                if field_name == 'selected_pollutant': 
                    new_value = json.loads(new_value_str)
                elif field_name == 'selected_reduction_target':
                    selected_dict = {0: 'EOS', 1:'EOR', 2: 'EOT'}
                    new_value = selected_dict[int(new_value_str)]
                elif new_value_str in ('nitrogen', 'phosphorus', 'sediments', 'oxygen'):
                    new_value = new_value_str
                else:
                    new_value = float(new_value_str)
            except:
                new_value= 0.0;
            # Update the Scenario instance
            update_scenario_loads_field(scenario_id, field_name, new_value)
            #Scenario.objects.filter(pk=scenario_id).update(current_acres=new_acres_value)
        return JsonResponse({'status': 'success', 'message': 'Successfully updated the field'})

    else:
        # Handle non-POST request or non-HTMX request
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def get_selected_states(areas):
        all_states_dict =  {state.abbreviation: state.id for state in State.objects.all()}
        states_list = []
        for area in areas:
            state = all_states_dict[area.state.lower()]
            if state not in states_list:
                states_list.append(state);
        return states_list;

class LoadsView(LoginRequiredMixin, TemplateView):
    template_name = 'step_2/loads_alpine.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scenario_id = self.kwargs.get('id')  # Assuming you're passing the ID in the URL
        scenario = Scenario.objects.get(pk=scenario_id)
        counties = scenario.base_scenario.geographic_areas.all()
        counties_list = ", ".join([county.name for county in counties])
        bmps = scenario.bmps
        manure_transport_bmps = False

        if 'target_items' in bmps.keys() and 'Manure Transport' in bmps['target_items'].keys():
            manure_transport_bmps = True
        loads = scenario.loads
        required_keys = ['total_nitrogen', 'nitrogen_pct', 'total_phosphorus', 'phosphorus_pct', 'total_sediments', 'sediments_pct', 'total_oxygen', 'oxygen_pct', 'selected_pollutant', 'total_budget', 'states', 'selected_reduction_target']
        n_to_oxygen = 16.325 
        p_to_oxygen = 38.503 
        if not all(key in loads for key in required_keys):
            base_scenario_data = scenario.base_scenario.data

            loads['sum_load_total'] = base_scenario_data['sum_load_total']
            loads['total_nitrogen'] = [int(base_scenario_data['sum_load_total'][0]), int(base_scenario_data['sum_load_total'][3]), int(base_scenario_data['sum_load_total'][6])]
            loads['nitrogen_pct'] = 30.0
            loads['total_phosphorus'] = [int(base_scenario_data['sum_load_total'][1]), int(base_scenario_data['sum_load_total'][4]), int(base_scenario_data['sum_load_total'][7])] 
            loads['phosphorus_pct'] = 30.0
            loads['total_sediments'] = [int(base_scenario_data['sum_load_total'][2]), int(base_scenario_data['sum_load_total'][5]), int(base_scenario_data['sum_load_total'][8])]
            loads['sediments_pct'] = 30.0

            loads['total_oxygen'] = [int(base_scenario_data['sum_load_total'][0]*n_to_oxygen + base_scenario_data['sum_load_total'][1]*p_to_oxygen),int(base_scenario_data['sum_load_total'][3]*n_to_oxygen+base_scenario_data['sum_load_total'][4]*p_to_oxygen),int(base_scenario_data['sum_load_total'][6]*n_to_oxygen + base_scenario_data['sum_load_total'][7]*p_to_oxygen)]
            loads['oxygen_pct'] = 30.0
            loads['selected_pollutant'] = ['nitrogen']
            loads['total_budget'] = 0.0 
            loads['states'] = base_scenario_data['states'] 
            loads['selected_reduction_target'] = 'EOS' 
            scenario.loads = loads
            scenario.save()

        # counties_list = [county.name for county in scenario.base_scenario.geographic_areas.all()]
        print("Counties: ", counties_list)
        context['counties'] = counties_list
        selected_inv_dict = {'EOS':0, 'EOR':1, 'EOT':2}
        selected_reduction_target = selected_inv_dict[loads['selected_reduction_target']]
        context['scenario_info'] = ScenarioInfo.objects.get(pk=scenario.scenario_info.id)
        context['current_stage'] = 2,
        context['previous_stage'] = 1,
        context['next_stage'] = 3,
        context['total_nitrogen'] = loads['total_nitrogen'] 
        context['nitrogen_pct'] = loads['nitrogen_pct'] 
        context['nitrogen'] = ((100-loads['nitrogen_pct'])/100.0)*loads['total_nitrogen'][selected_reduction_target]
        context['total_phosphorus'] = loads['total_phosphorus'] 
        context['phosphorus_pct'] = loads['phosphorus_pct'] 
        context['phosphorus'] = ((100-loads['phosphorus_pct'])/100.0)*loads['total_phosphorus'][selected_reduction_target]
        context['total_sediments'] = loads['total_sediments'] 
        context['sediments_pct'] = loads['sediments_pct'] 
        context['sediments'] = ((100-loads['sediments_pct'])/100.0)*loads['total_sediments'][selected_reduction_target]
        context['total_oxygen'] = loads['total_oxygen'] 
        context['oxygen_pct'] = loads['oxygen_pct'] 
        context['oxygen'] = ((100-loads['oxygen_pct'])/100.0)*loads['total_oxygen'][selected_reduction_target]
        context['scenario_id'] = scenario_id
        context['selected_pollutant'] = loads['selected_pollutant'] 
        context['total_budget'] = loads['total_budget']
        context['my_total_nitrogen'] =  [int(loads['sum_load_total'][0]), int(loads['sum_load_total'][3]), int(loads['sum_load_total'][6])]
        context['selected_reduction_target'] = selected_reduction_target 
        context['manure_transport_bmps'] = manure_transport_bmps

        return context

class LoadsExecView(LoginRequiredMixin, TemplateView):
    template_name = 'step_2/loads_by_exec.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        execution_id = self.kwargs.get('id')  # Assuming you're passing the ID in the URL
        execution = Execution.objects.get(pk=execution_id)
        loads = execution.loads
        required_keys = ['total_nitrogen', 'nitrogen_pct', 'total_phosphorus', 'phosphorus_pct', 'total_sediments', 'sediments_pct', 'total_oxygen', 'oxygen_pct', 'selected_pollutant', 'total_budget', 'states', 'selected_reduction_target']

        selected_inv_dict = {'EOS':0, 'EOR':1, 'EOT':2}
        selected_reduction_target = selected_inv_dict[loads['selected_reduction_target']]
        context['scenario_info'] = ScenarioInfo.objects.get(pk=execution.scenario.scenario_info.id)
        context['current_stage'] = 2,
        context['previous_stage'] = 1,
        context['next_stage'] = 3,
        context['total_nitrogen'] = loads['total_nitrogen'] 
        context['nitrogen_pct'] = loads['nitrogen_pct'] 
        context['nitrogen'] = ((100-loads['nitrogen_pct'])/100.0)*loads['total_nitrogen'][selected_reduction_target]
        context['total_phosphorus'] = loads['total_phosphorus'] 
        context['phosphorus_pct'] = loads['phosphorus_pct'] 
        context['phosphorus'] = ((100-loads['phosphorus_pct'])/100.0)*loads['total_phosphorus'][selected_reduction_target]
        context['total_sediments'] = loads['total_sediments'] 
        context['sediments_pct'] = loads['sediments_pct'] 
        context['sediments'] = ((100-loads['sediments_pct'])/100.0)*loads['total_sediments'][selected_reduction_target]
        context['total_oxygen'] = loads['total_oxygen'] 
        context['oxygen_pct'] = loads['oxygen_pct'] 
        context['oxygen'] = ((100-loads['oxygen_pct'])/100.0)*loads['total_oxygen'][selected_reduction_target]
        context['execution_id'] =execution_id 
        context['selected_pollutant'] = loads['selected_pollutant'] 
        context['total_budget'] = loads['total_budget']
        context['my_total_nitrogen'] =  [int(loads['sum_load_total'][0]), int(loads['sum_load_total'][3]), int(loads['sum_load_total'][6])]
        context['selected_reduction_target'] = selected_reduction_target 

        return context

