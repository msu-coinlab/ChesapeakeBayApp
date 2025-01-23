from django.shortcuts import render
import pandas as pd
import json

from django.http import JsonResponse
import os
from django.shortcuts import render
from django.views.generic import TemplateView
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, ListView
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import ScenarioInfo, Scenario, BaseScenario, GeographicArea, State, Execution, Solution, Sector
from .tables import ExecutionCustomDataTable
#from .filters import ScenarioInfoFilter, ScenarioFilter
from .forms import ExecutionForm 
from core.tasks import process_new_base_scenario
from core.models import Bmp, BmpCategory,  BmpType
from .filters import ExecutionFilter
from solution.views import get_solutions
from django.http import Http404

from core.tasks import retrieve_optimization_solutions

def get_pareto_front(data_points_list, objective_0, objective_1):
    pareto_front = []
    
    # Flatten the list of lists (if it's not already flat)
    all_points = [point for sublist in data_points_list for point in sublist]
    
    for point in all_points:
        is_dominated = False
        for other_point in all_points:
            if other_point == point:
                # Don't compare a point with itself
                continue
            
            # Check if `point` is dominated by `other_point`
            if (other_point[objective_0] <= point[objective_0] and
                other_point[objective_1] <= point[objective_1] and
                (other_point[objective_0] < point[objective_0] or
                 other_point[objective_1] < point[objective_1])):
                is_dominated = True
                break
        
        if not is_dominated:
            # If `point` is not dominated by any other, add it to the Pareto front
            pareto_front.append(point)
    
    return pareto_front

def get_exec_solutions(scenario_id, selected_edge, selected_pollutant='N'):
    execs = []
    counter = 1
    data_points_list = []
    loads = Scenario.objects.get(pk=scenario_id).loads
    edge = {'EOS': 0, 'EOR': 1, 'EOT': 2}
    NT = loads['total_nitrogen'][edge[selected_edge]]
    PT = loads['total_phosphorus'][edge[selected_edge]]
    ST = loads['total_sediments'][edge[selected_edge]]

    for execution in Execution.objects.filter(scenario__id=scenario_id):
        nsolutions  = Solution.objects.filter(execution__id=execution.id).count()
        sums = {'Cost': 0, 'N': 0, 'P': 0, 'S': 0}
        counts = {'Cost': 0, 'N': 0, 'P': 0, 'S': 0}
        solutions = get_solutions(execution.id, selected_edge)

        data_points = [{
            'name': point['num'],
            'id': point['id'],
            'Cost': point['Cost'],
            'Pollutant': point[selected_pollutant],
            'N': point['N'],
            'P': point['P'],
            'S': point['S'],
            'NR': NT - point['N'],
            'PR': PT - point['P'],
            'SR': ST - point['S'],
            'NP': (NT - point['N'])*100/NT,
            'PP': (PT - point['P'])*100/PT,
            'SP': (ST - point['S'])*100/ST,
            'detail': point['id'],
            'execution_id': execution.id 
        } for point in solutions]
        data_points_list.append(data_points)

        for d in solutions:
            for key in sums.keys():
                sums[key] += d[key]
                counts[key] += 1

        avgs = {key: 0.0 if counts[key] == 0 else round(sums[key] / counts[key]) for key in sums.keys()}
        #avgs = {key: int(round(sums[key] / counts[key])) for key in sums}
        execs.append({ 'id': execution.id, 'execution': counter, 'solutions': nsolutions, 'avg_Cost': avgs['Cost'], 'avg_N': avgs['N'], 'avg_P': avgs['P'], 'avg_S': avgs['S'] }) 
        counter += 1

    return execs, data_points_list

class ListExecutions(LoginRequiredMixin, SingleTableMixin, ListView):
    model = Execution
    table_class = ExecutionCustomDataTable
    template_name = 'execution/list_executions_htmx.html'
    paginate_by = 25

    def get_context_data(self, **kwargs):
        ctx = super(ListExecutions, self).get_context_data(**kwargs)
        try:
            scenario_id = self.kwargs.get('id')
            scenario = Scenario.objects.get(pk=scenario_id)
            counties = scenario.base_scenario.geographic_areas.all()
            counties_list = ", ".join([county.name for county in counties])

            selected_edge = scenario.loads['selected_reduction_target']
            execs, data_points = get_exec_solutions(scenario_id, selected_edge)

            pareto_front = get_pareto_front(data_points, 'Cost', 'N')
            areas = scenario.base_scenario.geographic_areas.all()
            print("Base: ", list(scenario.base_scenario.data.keys()))
            print("Valid Loads: ", scenario.base_scenario.data['sum_load_total'])

            ctx['table'] = ExecutionCustomDataTable(execs)
            ctx['selected_edge'] = selected_edge
            ctx['data_points'] = json.dumps(data_points)
            ctx['pareto_front'] = json.dumps(pareto_front)
            ctx['total_cost'] = round(scenario.base_scenario.data['total_amount'], 2)
            ctx['sum_load_total'] = round(scenario.base_scenario.data['sum_load_total'][0], 2)
            ctx['page_title'] = f'Optimization Runs for {counties_list}: {scenario.scenario_info}'
            ctx['create_title'] = 'New Optimization Scenario'
            ctx['create_url'] = reverse('create_execution')
            ctx['scenario_id'] = scenario_id
        
        except Exception as e:
            raise Http404("Scenario not sent for optimization.")
        
        return ctx
    
    def get_queryset(self):
        """
        Overrides the default queryset to return executions filtered by the scenario_id
        captured from the URL.
        """
        scenario_id = self.kwargs.get('id')
        queryset = super().get_queryset().filter(scenario__id=scenario_id)
        return queryset

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        scenario_id = self.kwargs.get('id')
        # Check if the request is an HTMX request
        if 'HX-Request' in request.headers and 'name' in request.GET:

            name = request.GET.get('name', 'select-edge')  # Fetch the selected edge from the request
            print(name)
            if name == 'select-edge':
                selected_edge = request.GET.get('selected_edge', 'EOT')  # Fetch the selected edge from the request
                execution_id = self.kwargs.get('id')
                execs, data_points = get_exec_solutions(scenario_id, selected_edge)
                pareto_front = get_pareto_front(data_points, 'Cost', 'N')
                ctx = {} 
                ctx['data_points'] = json.dumps(data_points)
                ctx['pareto_front'] = json.dumps(pareto_front)
                #ctx['data_points'] = data_points
                #ctx['pareto_front'] = pareto_front
                return JsonResponse(ctx)

        else:
            return super().get(request, *args, **kwargs)
            #context = self.get_context_data(table=table, selected_edge=selected_edge, execution_id=execution_id, page_title='My Solutions')
            #html = render_to_string('solution/partials/_table.html', context, request=request)
            #return HttpResponse(html)

def count_rows_in_file(file_path):
    try:
        with open(file_path, 'r') as file:
            rows = file.readlines()
            # Count non-empty rows
            row_count = len([row for row in rows if row.strip()])
        return row_count
    except FileNotFoundError:
        return "File not found."

def get_first_values_from_file(file_path):
    print('in get_first_values', file_path)
    try:
        with open(file_path, 'r') as file:
            # Read each line, split by space, and get the first value
            first_values = [row.split()[0] for row in file if row.strip()]
            print(first_values)
        return first_values
    except FileNotFoundError:
        print("File not found.")
        return "File not found."
    
def load_json_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

class CreateExecution(LoginRequiredMixin, CreateView):
    model = Execution
    form_class = ExecutionForm
    #fields = ['description', 'refund_amount']
    template_name = 'execution/create_generic.html'

    def get_success_url(self):
        return reverse('list_executions')

    def form_invalid(self, form):
        # Custom behavior here
        # For example, logging the error
        print("Form is invalid! Errors:", form.errors)
        # Make sure to call the superclass's method as well to ensure the form is rendered with errors
        return super().form_invalid(form)

    def form_valid(self, form):

        scenario = form.cleaned_data.get('scenario')
        retrieve_optimization_solutions(4)

        '''
        loads = scenario.loads
        bmps = scenario.bmps
        costs = scenario.costs
        bmp_constraints = scenario.bmp_constraints
        advanced_constraints = scenario.advanced_constraints

        form.instance.loads = loads
        form.instance.bmps = bmps
        form.instance.costs = costs
        form.instance.bmp_constraints = bmp_constraints
        form.instance.advanced_constraints = advanced_constraints

    
        # Now save the Execution instance
        form.instance.save()

        path = '/home/gtoscano/projects/CastPSO/build/build/init_full_30_max_reduction/lc-an-all-previous/front'
        path = '/home/gtoscano/projects/CastPSO/build/build/init_full_30_max_reduction/lc-all-previous/front'
        pfront = f'{path}/pareto_front.txt'
        counter = count_rows_in_file(pfront)

        costs = get_first_values_from_file(pfront)
        submitted_land = {}
        submitted_animal = {}
        submitted_manuretransport = {}
        for i in range(counter):
            submmited_land_path = f'{path}/{i}_impbmpsubmittedland.json'
            if os.path.exists(submmited_land_path):
                submitted_land = load_json_data(submmited_land_path)

            submitted_animal_path = f'{path}/{i}_impbmpsubmittedanimal.json'
            if os.path.exists(submitted_animal_path):
                submitted_animal = load_json_data(submitted_animal_path)
            submitted_manuretransport_path = f'{path}/{i}_impbmpsubmittedmanuretransport.json'
            if os.path.exists(submitted_manuretransport_path):
                submitted_manuretransport = load_json_data(submitted_manuretransport_path)


            reportloads_path = f'{path}/{i}_reportloads.parquet'
            #['NLoadEos','PLoadEos','SLoadEos','NLoadEor','PLoadEor','SLoadEor','NLoadEot','PLoadEot','SLoadEot']
            df = pd.read_parquet(reportloads_path)
            
            # Columns to sum
            columns_to_sum = ['NLoadEos', 'PLoadEos', 'SLoadEos', 'NLoadEor', 'PLoadEor', 'SLoadEor', 'NLoadEot', 'PLoadEot', 'SLoadEot']

            # Grouping by 'SectorId' and summing the specified columns for each group
            loads_by_sector = df.groupby('SectorId')[columns_to_sum].sum().reset_index()
            
            # Summing the specified columns
            total_sum_by_columns = df[columns_to_sum].sum()
            objectives = [costs[i]] + total_sum_by_columns.tolist()

            total = {'Cost': float(objectives[0]), 'EOS': {'N': float(objectives[1]), 'P': float(objectives[2]), 'S': float(objectives[3])}, 'EOR': {'N': float(objectives[4]), 'P': float(objectives[5]), 'S': float(objectives[6])}, 'EOT': {'N': float(objectives[7]), 'P': float(objectives[8]), 'S': float(objectives[9])}} 

            sector_dict = {str(sector.id): f'{sector.name}' for sector in Sector.objects.all()}
            sector_names = [sector.name for sector in Sector.objects.all()]
            loads_dict = {}

            for index, loads in loads_by_sector.iterrows():
                sector_name = sector_dict[str(int(loads['SectorId']))]
                loads_dict[sector_name]  = {'Cost': float(0.0), 'EOS': {'N': float(loads['NLoadEos']), 'P': float(loads['PLoadEos']), 'S': float(loads['SLoadEos'])}, 'EOR': {'N': float(loads['NLoadEor']), 'P': float(loads['PLoadEor']), 'S': float(loads['SLoadEor'])}, 'EOT': {'N': float(loads['NLoadEot']), 'P': float(loads['PLoadEot']), 'S': float(loads['SLoadEot'])}}
            loads_dict['Total'] = total

            #execution = Execution.objects.create(scenario=form.instance.id, loads=loads, bmps=bmps, costs=costs, bmp_constraints=bmp_constraints, advanced_constraints=advanced_constraints)
            #execution.save()
            data = {'Loads': loads_dict, 'sector_names': sector_names}
            execution_instance = Execution.objects.get(id=form.instance.id)


            solution = Solution.objects.create(execution=execution_instance, land_json= submitted_land, animal_json=submitted_animal, manure_json=submitted_manuretransport, data=data) 

            solution.save()
        
    

    
        # Continue with the rest of the form handling
        '''
        return super(CreateExecution, self).form_valid(form)

class ViewExecution(LoginRequiredMixin, TemplateView):
    template_name = 'execution/view.html'
    model =Execution 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        execution_id = self.kwargs.get('id')  # Assuming you're passing the ID in the URL
        print(execution_id)

        execution = Execution.objects.get(id=execution_id)

        counties = execution.base_execution.geographic_areas.all()
        counties_list = [county.name for county in counties]

        context['execution_info'] = execution.base_execution.execution_info 
        context['counties'] = counties_list 
        context['execution_id'] = execution_id

               
        return context

