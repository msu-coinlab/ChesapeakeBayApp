from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import FileResponse, Http404
from django.core.files.base import ContentFile
from django.conf import settings
from django.views import View
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Q
from django.views.generic import TemplateView
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, ListView
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.http import HttpResponse
from django.template.loader import render_to_string
import pandas as pd
import plotly.express as px
from django.shortcuts import get_object_or_404
import os
import csv
from io import BytesIO

from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import OpenAI

import json
import random
import string
import numpy as np
from core.models import ScenarioInfo, Scenario, BaseScenario, GeographicArea, State, Solution, Solution, Execution
from .tables import EfficiencyBmpCustomDataTable, SolutionCustomDataTable, EfficiencyBmpCustomDataTable, AnimalBmpCustomDataTable, ManureBmpCustomDataTable, SolutionBySectorTable, SolutionBySectorTableSimple, EfficiencyBmpCustomDataTable2, AnimalBmpCustomDataTable2, SummaryEfficiencyBmpCustomDataTable, LoadsTable 
from .forms import SolutionForm 
from core.tasks import process_new_base_scenario, retrieve_optimization_solutions 
from core.models import Bmp, BmpCost, BmpCategory,  BmpType, Agency, Bmp, LoadSrc, AnimalGrp, Sector, LandRiverSegment


import umap.umap_ as umap


#bmp_dict = None
#load_src_dict =  None
#animal_dict = None
#county_dict = None
#county_dict2 = None
#sector_dict = None
#load_src_sector_dict = None
#lrs_dict = None


#def initialize_globals():
#    pass
#global bmp_dict, load_src_dict, animal_dict, county_dict, county_dict2, sector_dict, load_src_sector_dict, lrs_dict
#if bmp_dict is None:
#    pass
#agency_dict = {str(agency.id): agency.name for agency in Agency.objects.all()}
#bmp_dict = {str(bmp.id): bmp.name for bmp in Bmp.objects.all()}
#load_src_dict = {str(load_src.id): load_src.name for load_src in LoadSrc.objects.all()}
#animal_dict = {str(animal.id): animal.name for animal in AnimalGrp.objects.all()}
#county_dict = {str(county.county): f'{county.name}, {county.state}' for county in GeographicArea.objects.all()}
#county_dict2 = {str(county.county): f'{county.name}, {county.state}' for county in GeographicArea.objects.all()}
#sector_dict = {str(sector.id): f'{sector.name}' for sector in Sector.objects.all()}
#load_src_sector_dict = {str(load_src.id): load_src.sector.name for load_src in LoadSrc.objects.all()}
#lrs_dict = {str(lrs.id): lrs.name for lrs in LandRiverSegment.objects.all()}


# Define a simple class to represent a point
class Point:
    def __init__(self, name, x_value, y_value, detail):
        self.name = name
        self.x_value = x_value
        self.y_value = y_value
        self.detail = detail

# Function to generate a random name
def generate_random_name(length=5):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def htmx_random_points(request):
    # Generate random data points
    random_data = [{
        'name': f'Random {i}',
        'x': random.randint(1, 100),
        'y': random.randint(1, 100),
        'detail': f'Detail {i}'
    } for i in range(10)]  # Generate 10 random points

    # Return data as JSON (HTMX can handle JSON responses too)
    return JsonResponse(random_data, safe=False)
def scatter_plot(request):
    # Generate 100 random points
    data_points = [Point(
        name=generate_random_name(),
        x_value=random.uniform(-100, 100),
        y_value=random.uniform(-100, 100),
        detail=f"Detail about {generate_random_name()}"
    ) for _ in range(100)]
    
    # Use list comprehension to structure the data as specified
    data = [{
        'name': point.name,
        'x': point.x_value,
        'y': point.y_value,
        'detail': point.detail
    } for point in data_points]
    
    
    context = {
        'data_points': json.dumps(data) # Convert data to JSON to use in JavaScript
    }
    return render(request, 'solution/your_template.html', context)

def scatter_plot2(request):
    # Generate 100 random points
    data_points = [Point(
        name=generate_random_name(),
        x_value=random.uniform(-100, 100),
        y_value=random.uniform(-100, 100),
        detail=f"Detail about {generate_random_name()}"
    ) for _ in range(100)]
    
    # Use list comprehension to structure the data as specified
    data = [{
        'name': point.name,
        'x': point.x_value,
        'y': point.y_value,
        'detail': point.detail
    } for point in data_points]
    
    
    context = {
        'data_points': json.dumps(data) # Convert data to JSON to use in JavaScript
    }
    return render(request, 'solution/your_template3.html', context)


def scatter_plot3(request):
    
    execution_id = 10
    scenario_list = []
    scenario_list2 = []

    execution = Execution.objects.get(id=execution_id) 
    loads = execution.loads
    counter = 1
    for solution in Solution.objects.filter(
            Q(execution__id=execution_id),
            Q(added=False) | Q(added=True, evaluated=True)):
        labels = ['Cost', 'NLoadEos', 'PLoadEos', 'SLoadEos', 'NLoadEor', 'PLoadEor', 'SLoadEor', 'NLoadEot', 'PLoadEot', 'SLoadEot']
        data = solution.data
        objectives = data['objectives']

        loads_by_sector = data['loads_by_sector']
        scenario_data = {} 
        scenario_data2 = {} 
        sector_names = []
        for load_by_sector in loads_by_sector:
            #sector_name = sector_dict[str(load_by_sector['SectorId'])]
            sector_obj = Sector.objects.get(id=load_by_sector['SectorId'])
            sector_name = sector_obj.name
            sector_names.append(sector_name)
            scenario_data[sector_name]  = {'Cost': int(0.0), 'Eos': {'N': int(load_by_sector['NLoadEos']), 'P': int(load_by_sector['PLoadEos']), 'S': int(load_by_sector['SLoadEos'])}, 'Eor': {'N': int(load_by_sector['NLoadEor']), 'P': int(load_by_sector['PLoadEor']), 'S': int(load_by_sector['SLoadEor'])}, 'Eot': {'N': int(load_by_sector['NLoadEot']), 'P': int(load_by_sector['PLoadEot']), 'S': int(load_by_sector['SLoadEot'])}}
        scenario_data['total2'] = {'Cost': int(float(objectives[0])), 'Eos': {'N': int(100*float(objectives[1])/float(loads['sum_load_total'][0])), 'P': int(float(objectives[2])/float(loads['sum_load_total'][0])), 'S': int(float(objectives[3]))}, 'Eor': {'N': int(float(objectives[4])), 'P': int(float(objectives[5])), 'S': int(float(objectives[6]))}, 'Eot': {'N': int(float(objectives[7])), 'P': int(float(objectives[8])), 'S': int(float(objectives[9]))}} 
        scenario_data['total'] = {'Cost': int(float(objectives[0])), 'Eos': {'N': int(float(objectives[1])), 'P': int(float(objectives[2])), 'S': int(float(objectives[3]))}, 'Eor': {'N': int(float(objectives[4])), 'P': int(float(objectives[5])), 'S': int(float(objectives[6]))}, 'Eot': {'N': int(float(objectives[7])), 'P': int(float(objectives[8])), 'S': int(float(objectives[9]))}} 
        scenario_data['sector_names'] = sector_names
        scenario_data['id'] = counter 
        scenario_data2['sector_names'] = sector_names
        scenario_data2['id'] = counter 
        scenario_list.append(scenario_data)
        scenario_list2.append(scenario_data2)
        counter += 1

    base_loads = {'name': 'Base Scenario', 'Cost': int(float(0.0)), 'Eos': {'N': int(float(loads['sum_load_total'][0])), 'P': int(float(loads['sum_load_total'][1])), 'S': int(float(loads['sum_load_total'][2]))}, 'Eor': {'N': int(float(loads['sum_load_total'][3])), 'P': int(float(loads['sum_load_total'][4])), 'S': int(float(loads['sum_load_total'][0]))}, 'Eot': {'N': int(float(loads['sum_load_total'][0])), 'P': int(float(loads['sum_load_total'][0])), 'S': int(float(loads['sum_load_total'][0]))}}
    context = {
        'data_points': json.dumps(scenario_list), # Convert data to JSON to use in JavaScript
        'data_points2': json.dumps(scenario_list2), # Convert data to JSON to use in JavaScript
        'edge_seleted': 'Eos',
        'pollutan_selected': 'N',
        'base_loads': json.dumps(base_loads),
    }
    return render(request, 'solution/your_template4.html', context)



class ListSolutionsAlpine(LoginRequiredMixin, SingleTableMixin, ListView):
    model = Solution
    table_class = SolutionCustomDataTable
    template_name = 'solution/list_table_generic_alpine.html'
    paginate_by = 25 

    def get_context_data(self, **kwargs):
        ctx = super(ListSolutionsAlpine, self).get_context_data(**kwargs)
        execution_id = self.kwargs.get('id')
        solutions = []
        selected_edge = 'EOS'
        edge_options = ['EOS', 'EOR', 'EOT']
        
        data_list = []
        for solution in Solution.objects.filter(
            Q(execution__id=execution_id),
            Q(added=False) | Q(added=True, evaluated=True)):
            data = solution.data
            data_tmp = data['Loads']['Total']
            data_tmp['id'] = solution.id
            data_tmp['actions'] = '<a href="/solution/view_by_sector/{}/" style="color: green;"><i class="material-icons">edit</i></a> <a href="/solution/view/{}/" style="color: green;"><i class="material-icons">play_arrow</i></a>'.format(solution.id, solution.id) 
            data_list.append(data_tmp)

        ctx['edge_options'] = edge_options
        ctx['load_data'] = data_list 
        ctx['selected_edge'] = selected_edge
        ctx['page_title'] = 'Optimized Solutions'
        ctx['execution_id'] = execution_id 
        return ctx

def get_solutions(execution_id, selected_edge):
    counter = 1
    solutions = []

    for solution in Solution.objects.filter(
        Q(execution__id=execution_id),
        Q(added=False) | Q(added=True, evaluated=True)):

        data = solution.data
        totals = data['Loads']['Total'][selected_edge]
        totals['num'] = counter 
        totals['id'] = solution.id 
        totals['Cost'] = data['Loads']['Total']['Cost']
        totals['execution_id'] = execution_id
        solutions.append(totals)
        counter += 1
    return solutions

def get_solution_by_sector(execution_id, selected_edge, solution_id, counter):

    solution = Solution.objects.filter(execution__id=execution_id , id=solution_id).first()
    if solution is None: 
        return None
    data = solution.data
    sector_names = data.get('sector_names', [])
    rows = {} 
    for sector_name in sector_names:
        row = {key: int(round(value)) for key, value in (data['Loads'][sector_name][selected_edge]).items()}
    
        row['Cost'] = int(round(data['Loads'][sector_name]['Cost']))
        rows[sector_name]= row
    rows['num'] =  counter
    rows['id'] = solution.id
    return rows 

def get_solutions_by_sector(execution_id, selected_edge):
    counter = 1
    solutions = []
    for solution in Solution.objects.filter(
        Q(execution__id=execution_id),
        Q(added=False) | Q(added=True, evaluated=True)):
        obtained_solution = get_solution_by_sector(execution_id, selected_edge, solution.id, counter)
        if obtained_solution is not None:
            solutions.append(obtained_solution)
            counter += 1
    return solutions


def update_scenario_loads_field(scenario_id, field_name, new_value):
    # Update the field using a dictionary
    scenario = get_object_or_404(Scenario, pk=scenario_id)
    scenario.loads[field_name] = new_value
    scenario.save()

@require_POST
def update_(request):
    data = request.POST
    try:
        print(data)
        pass
    except Exception as e:
        print(e)
        return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'success'})

class ListSolutionsHTMX(LoginRequiredMixin, SingleTableMixin, ListView):
    model = Solution
    table_class = SolutionCustomDataTable
    template_name = 'solution/list_table_generic_htmx.html'
    paginate_by = 25 

    def get_context_data(self, **kwargs):
        ctx = super(ListSolutionsHTMX, self).get_context_data(**kwargs)
        execution_id = self.kwargs.get('id')
        scenario = Scenario.objects.get(pk=execution_id)

        #retrieve_optization_solutions(23)
        execution = Execution.objects.get(id=execution_id)
        selected_edge = execution.loads['selected_reduction_target']
        selected_pollutant = 'N'
        solutions = get_solutions(execution_id, selected_edge)
        solutions_by_sector = get_solutions_by_sector(execution_id, selected_edge)

        data_umap = np.array([[point['Cost'], point['N'], point['P'], point['S']] for point in solutions])
        #reducer = umap.UMAP()
        #embedding = reducer.fit_transform(data_umap)
        #embedding_lst = [{'x': row[0], 'y': row[1]} for row in embedding]
        data_points = [{
            'name': point['num'],
            'id': point['id'],
            'Cost': point['Cost'],
            'Pollutant': point[selected_pollutant],
            'N': point['N'],
            'P': point['P'],
            'S': point['S'],
            'detail': point['id'],
            'execution_id': execution_id
        } for point in solutions]

        
        ctx['table'] = SolutionCustomDataTable(solutions)
        ctx['selected_edge'] = selected_edge
        ctx['data_points'] = json.dumps(data_points)
        #ctx['data_points2'] = json.dumps(embedding_lst)
        ctx['sum_load_total'] = round(scenario.base_scenario.data['sum_load_total'][0], 2)
        ctx['page_title'] = 'Optimized Solutions'
        ctx['execution_id'] = execution_id 
        return ctx

    def get_queryset(self):
        execution_id = self.kwargs.get('id')
        queryset = super().get_queryset().filter(execution__id=execution_id)
        return queryset

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        # Check if the request is an HTMX request
        if 'HX-Request' in request.headers and 'name' in request.GET:

            name = request.GET.get('name', 'select-edge')  # Fetch the selected edge from the request
            if name == 'select-edge':
                selected_edge = request.GET.get('selected_edge', 'EOT')  # Fetch the selected edge from the request
                execution_id = self.kwargs.get('id')
                solutions = get_solutions(execution_id, selected_edge)
                table = SolutionCustomDataTable(solutions)


                return render(request, 'solution/partials/_table.html', {'table': table})

            elif name == 'display-loads-by-sector': 
                selected_solution = request.GET.get('selected_solution', '1')
                selected_edge = request.GET.get('selected_edge', 'EOT')  # Fetch the selected edge from the request
                execution_id = self.kwargs.get('id')

                solution = get_solution_by_sector(execution_id, selected_edge, selected_solution, 0)
                if solution is None:
                    return super().get(request, *args, **kwargs)

                solution_by_sector_list = []
                sectors = ['Agriculture', 'Developed', 'Natural', 'Septic', 'Wastewater']
                total_N = 0
                total_P = 0
                total_S = 0
                for sector in sectors:
                    if sector in solution.keys():
                        row = solution[sector]
                        row['sector'] = sector
                        total_N += int(round(row['N']))
                        total_P += int(round(row['P']))
                        total_S += int(round(row['S']))
                        solution_by_sector_list.append(solution[sector])


                totals = {'sector': 'Total', 'N': total_N, 'P': total_P, 'S': total_S}
                table = SolutionBySectorTableSimple(solution_by_sector_list)
                return render(request, 'solution/partials/_table_with_foot.html', {'total_N': total_N, 'total_P': total_P, 'total_S':total_S, 'load_list': solution_by_sector_list})
            elif name == 'display-loads-by-sector2': 
                selected_solution = request.GET.get('selected_solution', '1')
                selected_edge = request.GET.get('selected_edge', 'EOT')
                execution_id = self.kwargs.get('id')
                return render(request, 'solution/partials/_table_with_foot.html', {'total_N': 0})

        else:
            return super().get(request, *args, **kwargs)
            #context = self.get_context_data(table=table, selected_edge=selected_edge, execution_id=execution_id, page_title='Optimized Solutions')
            #html = render_to_string('solution/partials/_table.html', context, request=request)
            #return HttpResponse(html)
def get_scenario_data(request):
    #initialize_globals()
    # This is a placeholder for your actual data retrieval logic
    execution_id = 10
    scenario_list = []

    for solution in Solution.objects.filter(
        Q(execution__id=execution_id),
        Q(added=False) | Q(added=True, evaluated=True)):
        labels = ['Cost', 'NLoadEos', 'PLoadEos', 'SLoadEos', 'NLoadEor', 'PLoadEor', 'SLoadEor', 'NLoadEot', 'PLoadEot', 'SLoadEot']
        data = solution.data
        objectives = data['objectives']

        loads_by_sector = data['loads_by_sector']
        counter = 1
        scenario_data = {} 
        sector_names = []
        for load_by_sector in loads_by_sector:
            #sector_name = sector_dict[str(load_by_sector['SectorId'])]
            sector_obj = Sector.objects.get(id=load_by_sector['SectorId'])
            sector_name = sector_obj.name
            sector_names.append(sector_name)
            scenario_data[sector_name]  = {'Cost': 0.0, 'Eos': {'N': load_by_sector['NLoadEos'], 'P': load_by_sector['PLoadEos'], 'S': load_by_sector['SLoadEos']}, 'Eor': {'N': load_by_sector['NLoadEor'], 'P': load_by_sector['PLoadEor'], 'S': load_by_sector['SLoadEor']}, 'Eot': {'N': load_by_sector['NLoadEot'], 'P': load_by_sector['PLoadEot'], 'S': load_by_sector['SLoadEot']}}
        scenario_data['total'] = {'Cost': float(objectives[0]), 'Eos': {'N': float(objectives[1]), 'P': float(objectives[2]), 'S': float(objectives[3])}, 'Eor': {'N': float(objectives[4]), 'P': float(objectives[5]), 'S': float(objectives[6])}, 'Eot': {'N': float(objectives[7]), 'P': float(objectives[8]), 'S': float(objectives[9])}} 
        scenario_data['sector_names'] = sector_names
        scenario_data['id'] = counter 
        scenario_list.append(scenario_data)
        counter += 1

    return JsonResponse(scenario_list, safe=False)  # Return the list of scenarios as JSON

class PlotSolutions(LoginRequiredMixin, ListView):
    #initialize_globals()
    model = Solution
    template_name = 'solution/plot_solutions.html'
    paginate_by = 25 

    def get_context_data(self, **kwargs):
        ctx = super(PlotSolutions, self).get_context_data(**kwargs)
        execution_id = self.kwargs.get('id')
        solutions = []
        counter = 1
        edge = ['Eos', 'Eor', 'Eot']
        axis = ['Cost', 'N', 'P', 'S']
        scenario_list = []
        for solution in Solution.objects.filter(
            Q(execution__id=execution_id),
            Q(added=False) | Q(added=True, evaluated=True)):
            labels = ['Cost', 'NLoadEos', 'PLoadEos', 'SLoadEos', 'NLoadEor', 'PLoadEor', 'SLoadEor', 'NLoadEot', 'PLoadEot', 'SLoadEot']
            data = solution.data
            objectives = data['objectives']

            loads_by_sector = data['loads_by_sector']
            counter = 1
            scenario_data = {} 
            sector_names = []
            for load_by_sector in loads_by_sector:
                #sector_name = sector_dict[str(load_by_sector['SectorId'])]
                sector_obj = Sector.objects.get(id=load_by_sector['SectorId'])
                sector_name = sector_obj.name
                sector_names.append(sector_name)
                scenario_data[sector_name]  = {'Cost': 0.0, 'Eos': {'N': load_by_sector['NLoadEos'], 'P': load_by_sector['PLoadEos'], 'S': load_by_sector['SLoadEos']}, 'Eor': {'N': load_by_sector['NLoadEor'], 'P': load_by_sector['PLoadEor'], 'S': load_by_sector['SLoadEor']}, 'Eot': {'N': load_by_sector['NLoadEot'], 'P': load_by_sector['PLoadEot'], 'S': load_by_sector['SLoadEot']}}
            scenario_data['total'] = {'Cost': float(objectives[0]), 'Eos': {'N': objectives[1], 'P': objectives[2], 'S': objectives[3]}, 'Eor': {'N': objectives[4], 'P': objectives[5], 'S': objectives[6]}, 'Eot': {'N': objectives[7], 'P': objectives[8], 'S': objectives[9]}} 
            scenario_data['sector_names'] = sector_names
            scenario_data['id'] = counter 
            scenario_list.append(scenario_data)
            counter += 1

        ctx['data'] =  scenario_list 
        ctx['edge_seleted'] = 'Eos'
        ctx['pollutan_selected'] = 'N'

        ctx['page_title'] = 'Optimized Solutions'
        ctx['create_title'] = 'New Solution'
        ctx['create_url'] = reverse('create_solution')
        ctx['execution_id'] =execution_id 
        return ctx

    def get_queryset(self):
        """
        Overrides the default queryset to return solutions filtered by the scenario_id
        captured from the URL.
        """
        execution_id = self.kwargs.get('id')
        queryset = super().get_queryset().filter(execution__id=execution_id)
        return queryset

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
    try:
        with open(file_path, 'r') as file:
            # Read each line, split by space, and get the first value
            first_values = [row.split()[0] for row in file if row.strip()]
        return first_values
    except FileNotFoundError:
        return "File not found."
def load_json_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


class ViewSolutionBySector(LoginRequiredMixin, TemplateView):
    template_name = 'solution/view_solution_by_sector.html'
    model =Solution 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        solution_id = self.kwargs.get('id')  # Assuming you're passing the ID in the URL

        solution = Solution.objects.get(
            Q(id=solution_id),
            Q(added=False) | Q(added=True, evaluated=True))
        data = solution.data
        edge_options = ['EOS', 'EOR', 'EOT']
        selected_edge = 'EOS'
        loads = data['Loads']
        counter = 1
        loads_list = []
        for key, value in loads.items(): 
            row = value[selected_edge]
            row['id'] = counter
            row['sector'] = key
            loads_list.append(row)

            counter += 1

        context['table'] = SolutionBySectorTable(loads_list)
        context['solution_id'] = solution_id
        context['edge_options'] = edge_options
        context['selected_edge'] = selected_edge

               
        return context


               
        return context
class PlotySolutions(LoginRequiredMixin, TemplateView):
    template_name = 'solution/view_solution_by_sector.html'
    model =Solution 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        solution_id = self.kwargs.get('id')  # Assuming you're passing the ID in the URL

        solution = Solution.objects.get(
            Q(id=solution_id),
            Q(added=False) | Q(added=True, evaluated=True))
        data = solution.data
        edge = ['EOS', 'EOR', 'EOT']
        selected_edge = 'EOS'
        loads = data['Loads']
        counter = 1
        loads_list = []
        for key, value in loads.items(): 
            row = value[selected_edge]
            row['id'] = counter
            row['sector'] = key
            loads_list.append(row)

            counter += 1

        context['table'] = SolutionBySectorTable(loads)
        context['solution_id'] = solution_id

               
        return context


def get_land_bmps_by_sector_county(land_bmps):
        #initialize_globals()
        counter = 1
        costs = {}
        efficiency_summary = {}
        county_name_dics = {}
        geo_jsons = {} 
        for key, value in land_bmps.items():
            result_list = key.split("_")
            lrs = result_list[0]
            #sector = load_src_sector_dict[result_list[2]]
            load_src_obj = LoadSrc.objects.get(id=result_list[2])
            sector = load_src_obj.sector.name
            bmp = Bmp.objects.get(id=result_list[3]).name
            #bmp = bmp_dict[result_list[3]]
            lrs_item =  LandRiverSegment.objects.get(id=lrs)
            geographic_area = lrs_item.geographic_area
            county_name = f'{geographic_area.name}, {geographic_area.state}' 
            county_name_dics[county_name] = geographic_area.id
            if county_name not in geo_jsons.keys():
                geo_jsons[county_name] = geographic_area.geo_data


            if county_name in efficiency_summary.keys():
                if bmp in efficiency_summary[county_name].keys():
                    efficiency_summary[county_name][bmp] += value 
                else:
                    efficiency_summary[county_name][bmp] = value
            else:
                efficiency_summary[county_name] = { bmp : value}

            if sector in costs.keys():
                costs[sector] += 1 
            else:
                costs[sector] = 1 
            counter += 1
        efficiency_summary_list = []
        counter = 1
        for key, value in efficiency_summary.items():
            for bmp, amount in value.items():
                efficiency_summary_list.append({'id': counter, 'county': key, 'bmp': bmp, 'amount': amount})
                counter += 1

        return efficiency_summary_list, costs, geo_jsons




def get_bmps_by_sector(land_bmps, animal_bmps, manure_bmps):
        #initialize_globals()
        counter = 1
        efficiency = []
        costs = {}
        efficiency_summary = {}
        county_name_dics = {}
        geo_jsons = {} 
        lrs_geo_jsons = {}
        for key, value in land_bmps.items():
            result_list = key.split("_")
            lrs = result_list[0]
            agency = Agency.objects.get(id=result_list[1]).name
            #agency = agency_dict[result_list[1]]

            load_src = LoadSrc.objects.get(id=result_list[2]).name
            #load_src = load_src_dict[result_list[2]]
            #sector = load_src_sector_dict[result_list[2]]
            load_src_obj = LoadSrc.objects.get(id=result_list[2])
            sector = load_src_obj.sector.name
            bmp_id = result_list[3]
            bmp = Bmp.objects.get(id=result_list[3]).name
            #bmp = bmp_dict[result_list[3]]
            lrs_obj = LandRiverSegment.objects.get(id=lrs)
            efficiency.append({'id': counter, 'lrs': lrs_obj.name, 'agency': agency, 'load_src': load_src, 'sector': sector, 'bmp': bmp, 'amount': value})
            # Convert the LRS to a county
            lrs_item =  LandRiverSegment.objects.get(id=lrs)
            if lrs_item.name not in lrs_geo_jsons.keys():
                lrs_geo_jsons[lrs_item.name] = lrs_item.geo_data


            geographic_area = lrs_item.geographic_area


            county_name = f'{geographic_area.name}, {geographic_area.state}' 
            county_name_dics[county_name] = geographic_area.id
            if county_name not in geo_jsons.keys():
                geo_jsons[county_name] = geographic_area.geo_data


            if county_name in efficiency_summary.keys():
                if bmp in efficiency_summary[county_name].keys():
                    efficiency_summary[county_name][bmp_id] += value 
                else:
                    efficiency_summary[county_name][bmp_id] = value
            else:
                efficiency_summary[county_name] = { bmp_id : value}

            if sector in costs.keys():
                costs[sector] += 1 
            else:
                costs[sector] = 1 
            counter += 1
        efficiency_summary_list = []
        counter = 1
        features = [] 
        for key, value in efficiency_summary.items():
            for bmp_id, amount in value.items():
                this_bmp = Bmp.objects.get(id=bmp_id)
                efficiency_summary_list.append({'id': counter, 'county': key, 'bmp': this_bmp.name, 'amount': round(amount,2), 'sector': this_bmp.sector.name})
                counter += 1

        counter = 1
        animal = [] 
        animal_summary = {}
        for key, value in animal_bmps.items():
            result_list = key.split("_")

            base_condition= result_list[0]
            county_id = result_list[1]
            print(county_id)
            county = GeographicArea.objects.get(county=int(county_id))
            #load_src_id = result_list[2]
            #load_src = load_src_dict[load_src_id]
            load_src = LoadSrc.objects.get(id=result_list[2]).name
            sector_id = result_list[2]
            #sector = load_src_sector_dict[sector_id]
            load_src_obj = LoadSrc.objects.get(id=result_list[2])
            sector = load_src_obj.sector.name
            animal_type = AnimalGrp.objects.get(id=result_list[3]).name
            #animal_id = result_list[3]
            #animal_type = animal_dict[animal_id]

            #bmp_id = result_list[4]
            #bmp = bmp_dict[bmp_id]
            bmp = Bmp.objects.get(id=result_list[4]).name


            state_abbr = county.state

            state_id = State.objects.get(abbreviation=state_abbr.lower()).id
            price = float(BmpCost.objects.filter(Q(state__id=state_id), Q(bmp__id=bmp_id)).first().cost)
            cost = price * value

            animal.append({'id': counter, 'base_condition': base_condition, 'state': (state_abbr).upper(), 'county_id': county_id, 'county': county.name, 'load_src_id': load_src_id, 'load_src': load_src, 'sector_id': sector_id, 'sector': sector, 'animal': animal_id, 'animal': animal_type, 'bmp_id': bmp_id, 'bmp': bmp, 'amount': value, 'price': price, 'cost': cost})


            if county in animal_summary.keys():
                if bmp in animal_summary[county].keys():
                    animal_summary[county][bmp] += value 
                else:
                    animal_summary[county][bmp] = value
            else:
                animal_summary[county] = { bmp : value}

            if sector in costs.keys():
                costs[sector] += 1 
            else:
                costs[sector] = 1 
            counter += 1
        animal_summary_list = []
        for key, value in animal_summary.items():
            for bmp, amount in value.items():
                animal_summary_list.append({'county': key, 'bmp': bmp, 'amount': amount})


        counter = 1
        manure = [] 
        manure_summary = {}
        for key, value in manure_bmps.items():
            result_list = key.split("_")


            #county_dict = {str(county.county): f'{county.name}, {county.state}' for county in GeographicArea.objects.all()}
            #county_from= county_dict[result_list[0]]
            #county_to = county_dict[result_list[1]]
            county_from_obj = GeographicArea.objects.get(county=result_list[0])
            county_from = f'{county_from_obj.name}, {county_from_obj.state}'

            county_to_obj = GeographicArea.objects.get(county=result_list[1])
            county_to = f'{county_to_obj.name}, {county_to_obj.state}'

            #load_src = load_src_dict[result_list[2]]
            load_src = LoadSrc.objects.get(id=result_list[2]).name
            #sector = load_src_sector_dict[result_list[2]]
            load_src_obj = LoadSrc.objects.get(id=result_list[2])
            sector = load_src_obj.sector.name

            animal_type = AnimalGrp.objects.get(id=result_list[3]).name
            #animal_id = animal_dict[result_list[3]]

            bmp = Bmp.objects.get(id=result_list[4]).name
            #bmp = bmp_dict[result_list[4]]

            manure.append({'id': counter, 'county_from': county_from, 'county_to': county_to, 'load_src': load_src, 'sector': sector, 'animal': animal_id, 'bmp': bmp, 'amount': value})

            if bmp in manure_summary.keys():
                manure_summary[bmp] += value 
            else:
                manure_summary[bmp] = value
            if sector in costs.keys():
                costs[sector] += 1 
            else:
                costs[sector] = 1 
            counter += 1
        manure_summary_list = []
        #for key, value in manure_summary.items():
        #    for bmp, amount in value.items():
        #        manure_summary_list.append({'county': key, 'bmp': bmp, 'amount': amount})
        return efficiency, efficiency_summary_list, animal, animal_summary, manure, manure_summary, costs, geo_jsons, lrs_geo_jsons


def get_geo_jsons(land_bmps):
        counter = 1
        geo_jsons = {} 
        lrs_geo_jsons = {}
        for key, _ in land_bmps.items():
            result_list = key.split("_")
            lrs = result_list[0]
            lrs_item =  LandRiverSegment.objects.get(id=lrs)
            if lrs_item.name not in lrs_geo_jsons.keys():
                lrs_geo_jsons[lrs_item.name] = lrs_item.geo_data


            geographic_area = lrs_item.geographic_area


            county_name = f'{geographic_area.name}, {geographic_area.state}' 
            if county_name not in geo_jsons.keys():
                geo_jsons[county_name] = geographic_area.geo_data

            counter += 1
        return  geo_jsons, lrs_geo_jsons

class ViewSolution_working(LoginRequiredMixin, TemplateView):
    template_name = 'solution/view_solution_htmx.html'
    model =Solution 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        solution_id = self.kwargs.get('id')  # Assuming you're passing the ID in the URL

        solution = Solution.objects.get(id=solution_id)
        for area in solution.execution.scenario.base_scenario.geographic_areas.all():
            print(area.name)

        land_bmps = solution.land_json
        animal_bmps = solution.animal_json
        manure_bmps = solution.manure_json

        efficiency, efficiency_summary, animal, animal_summary, manure, manure_summary, costs, geo_jsons, lrs_geo_jsons = get_bmps_by_sector(land_bmps, animal_bmps, manure_bmps)

        geojson = {"type": "FeatureCollection", "features": [{"id": "0", "type": "Feature", "properties": 1}] 
                   }
        context['summary_efficiency']= efficiency_summary 
        file_path = os.path.join(settings.BASE_DIR, 'static/reduced-mapshaper-chesapeake-states.geojson')
        file_path = os.path.join(settings.BASE_DIR, 'static/chesapeake-states.geojson')
        with open(file_path, 'r') as file:
            states_geojson = json.load(file)
        file_path = os.path.join(settings.BASE_DIR, 'static/reduced-mapshaper-chesapeake.geojson')
        with open(file_path, 'r') as file:
            chesapeake_geojson = json.load(file)
        file_path = os.path.join(settings.BASE_DIR, 'static/reduced-mapshaper-counties.geojson')
        with open(file_path, 'r') as file:
            county_geojson = json.load(file)

        county_list_of_features = [value for key, value in geo_jsons.items()] 
        lrs_list_of_features = [value for key, value in lrs_geo_jsons.items()] 

        county_alternative_geojson = {"type":"FeatureCollection","features":county_list_of_features}
        lrs_alternative_geojson = {"type":"FeatureCollection","features":lrs_list_of_features}

        print(lrs_alternative_geojson)

        context['scen_lrs_geojson_data'] =  lrs_alternative_geojson 
        context['scen_county_geojson_data'] =  county_alternative_geojson 
        context['county_geojson_data'] = county_geojson
        context['states_geojson_data'] = states_geojson
        context['chesapeake_geojson_data'] = chesapeake_geojson
        context['table'] = EfficiencyBmpCustomDataTable(efficiency)
        context['table2'] = AnimalBmpCustomDataTable(animal)
        context['table3'] = SummaryEfficiencyBmpCustomDataTable(efficiency_summary)

        #context['table3'] = ManureBmpCustomDataTable(manure)
        context['page_title'] = 'Proposed BMPs'
        context['solution_id'] = solution_id

        return context

class ViewSolution(LoginRequiredMixin, TemplateView):
    template_name = 'solution/view_solution_htmx.html'
    model =Solution 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        solution_id = self.kwargs.get('id')  # Assuming you're passing the ID in the URL

        solution = Solution.objects.get(id=solution_id)
        base_scenario = solution.execution.scenario.base_scenario
        df_base_reportloads = pd.read_parquet(base_scenario.reportloads_file.path)
        df_reportloads = pd.read_parquet(solution.reportloads_file.path)
        df_sector_loads = pd.read_parquet(solution.sector_loads_file.path)

        columns_to_sum = ['amount', 'Ns', 'Ps', 'Ss', 'Nr', 'Pr', 'Sr', 'Nt', 'Pt', 'St']
        df_sector_loads = df_sector_loads.groupby(['state', 'county', 'lrs', 'sector'])[columns_to_sum].sum().reset_index()

        land_bmps = solution.land_json
        geo_jsons, lrs_geo_jsons = get_geo_jsons(land_bmps)

        file_path = os.path.join(settings.BASE_DIR, 'static/reduced-mapshaper-chesapeake-states.geojson')
        file_path = os.path.join(settings.BASE_DIR, 'static/chesapeake-states.geojson')
        with open(file_path, 'r') as file:
            states_geojson = json.load(file)
        file_path = os.path.join(settings.BASE_DIR, 'static/reduced-mapshaper-chesapeake.geojson')
        with open(file_path, 'r') as file:
            chesapeake_geojson = json.load(file)
        file_path = os.path.join(settings.BASE_DIR, 'static/reduced-mapshaper-counties.geojson')
        with open(file_path, 'r') as file:
            county_geojson = json.load(file)

        if solution.land_file:
            df_efficiency = pd.read_parquet(solution.land_file.path)
            df_efficiency_summary = df_efficiency.groupby(['bmp'])['acres'].sum().reset_index()
            df_efficiency_summary.rename(columns={'acres': 'amount'}, inplace=True)
        else:
            df_efficiency = pd.DataFrame()
            df_efficiency_summary = pd.DataFrame()

        efficiency_summary_json = df_efficiency_summary.to_dict(orient='records')
        # check if animal_file exists
        if solution.animal_file:
            df_animal = pd.read_parquet(solution.animal_file.path)
            df_animal_summary = df_animal.groupby(['bmp'])['amount'].sum().reset_index()
        else:
            df_animal = pd.DataFrame()
            df_animal_summary = pd.DataFrame()
        animal_summary_json = df_animal_summary.to_dict(orient='records')
        # check if manure_file exists
        if solution.manure_file:
            df_manure = pd.read_parquet(solution.manure_file.path)
            df_manure_summary = df_manure.groupby(['bmp'])['amount'].sum().reset_index()
        else:
            df_manure = pd.DataFrame()
            df_manure_summary = pd.DataFrame()
        manure_summary_json = df_manure_summary.to_dict(orient='records')

        bmp_summary_json = efficiency_summary_json + animal_summary_json + manure_summary_json

        animal = df_animal.to_dict(orient='records')
        manure = df_manure.to_dict(orient='records')

        json_efficiency = df_efficiency.to_dict(orient='records')

        county_list_of_features = [value for key, value in geo_jsons.items()] 
        lrs_list_of_features = [value for key, value in lrs_geo_jsons.items()] 
        lrs_list_of_features2 = [] 
        counties_lrs = {}
        for key, value in lrs_geo_jsons.items():
            if value['properties']['GeographyType'] == 'lrs':
                # add all df_efficiency column Cost where lrs = key
                county_id = value['properties']['CountyId']
                loads = df_reportloads[df_reportloads['LrsegId'] == value['properties']['Id']].sum()
                base_loads = df_base_reportloads[df_base_reportloads['LrsegId'] == value['properties']['Id']].sum()
                pct_reduction = 100 - (loads / base_loads * 100)
                cost = df_efficiency[df_efficiency['lrs'] == key]['cost'].sum()
                acres = df_efficiency[df_efficiency['lrs'] == key]['acres'].sum()
                row = value
                row['properties']['Cost'] = int(round(cost,0))
                row['properties']['Acres'] = int(round(acres,0))
                row['properties']['Ns'] = int(round(loads['NLoadEos'],0))
                row['properties']['Ps'] = int(round(loads['PLoadEos'],0))
                row['properties']['Ss'] = int(round(loads['SLoadEos'],0))
                row['properties']['Nr'] = int(round(loads['NLoadEor'],0))
                row['properties']['Pr'] = int(round(loads['PLoadEor'],0))
                row['properties']['Sr'] = int(round(loads['SLoadEor'],0))
                row['properties']['Nt'] = int(round(loads['NLoadEot'],0))
                row['properties']['Pt'] = int(round(loads['PLoadEot'],0))
                row['properties']['St'] = int(round(loads['SLoadEot'],0))
                row['properties']['PN'] = int(round(pct_reduction['NLoadEos'],0))
                row['properties']['PP'] = int(round(pct_reduction['PLoadEos'],0))
                row['properties']['PS'] = int(round(pct_reduction['SLoadEos'],0))

                lrs_list_of_features2.append(row)
                if county_id in counties_lrs.keys():
                    counties_lrs[county_id]['Cost'] += cost
                    counties_lrs[county_id]['Acres'] += acres
                    counties_lrs[county_id]['Ns'] += loads['NLoadEos']
                    counties_lrs[county_id]['Ps'] += loads['PLoadEos']
                    counties_lrs[county_id]['Ss'] += loads['SLoadEos']
                    counties_lrs[county_id]['Nr'] += loads['NLoadEor']
                    counties_lrs[county_id]['Pr'] += loads['PLoadEor']
                    counties_lrs[county_id]['Sr'] += loads['SLoadEor']
                    counties_lrs[county_id]['Nt'] += loads['NLoadEot']
                    counties_lrs[county_id]['Pt'] += loads['PLoadEot']
                    counties_lrs[county_id]['St'] += loads['SLoadEot']
                    counties_lrs[county_id]['BN'] += base_loads['NLoadEos']
                    counties_lrs[county_id]['BP'] += base_loads['PLoadEos']
                    counties_lrs[county_id]['BS'] += base_loads['SLoadEos']
                else:
                    counties_lrs[county_id] = {'Cost': cost, 'Acres': acres, 'Ns': loads['NLoadEos'], 'Ps': loads['PLoadEos'], 'Ss': loads['SLoadEos'], 'Nr': loads['NLoadEor'], 'Pr': loads['PLoadEor'], 'Sr': loads['SLoadEor'], 'Nt': loads['NLoadEot'], 'Pt': loads['PLoadEot'], 'St': loads['SLoadEot'], 'BN': base_loads['NLoadEos'], 'BP': base_loads['PLoadEos'], 'BS': base_loads['SLoadEos']} 

        lrs_list_of_features2 = [] 
        for key, value in geo_jsons.items():
            if value['properties']['GeographyType'] == 'geographic_area':
                data = counties_lrs[value['properties']['Id']]
                # extend value with data 
                value['properties']['Cost'] = int(round(data['Cost'],0))
                value['properties']['Acres'] = int(round(data['Acres'],0))
                value['properties']['Ns'] = int(round(data['Ns'],0))
                value['properties']['Ps'] = int(round(data['Ps'],0))
                value['properties']['Ss'] = int(round(data['Ss'],0))
                value['properties']['Nr'] = int(round(data['Nr'],0))
                value['properties']['Pr'] = int(round(data['Pr'],0))
                value['properties']['Sr'] = int(round(data['Sr'],0))
                value['properties']['Nt'] = int(round(data['Nt'],0))
                value['properties']['Pt'] = int(round(data['Pt'],0))
                value['properties']['St'] = int(round(data['St'],0))
                value['properties']['PN'] = int(round(100-(data['Ns']/data['BN']) * 100))
                value['properties']['PP'] = int(round(100-(data['Ps']/data['BP']) * 100))
                value['properties']['PS'] = int(round(100-(data['Ss']/data['BS']) * 100))
                lrs_list_of_features2.append(value)

        county_alternative_geojson = {"type":"FeatureCollection","features":county_list_of_features}
        lrs_alternative_geojson = {"type":"FeatureCollection","features":lrs_list_of_features}


        #context['summary_efficiency']= efficiency_summary 
        context['scen_lrs_geojson_data'] =  lrs_alternative_geojson 
        context['scen_county_geojson_data'] =  county_alternative_geojson 
        context['county_geojson_data'] = county_geojson
        context['states_geojson_data'] = states_geojson
        context['chesapeake_geojson_data'] = chesapeake_geojson
        context['table0'] = SummaryEfficiencyBmpCustomDataTable(bmp_summary_json)
        context['table'] = EfficiencyBmpCustomDataTable(json_efficiency)
        context['table2'] = AnimalBmpCustomDataTable(animal)
        context['table3'] = ManureBmpCustomDataTable(manure)
        context['table4'] = LoadsTable(df_sector_loads.to_dict(orient='records'))
        context['summary_bmps_json'] = json.dumps(efficiency_summary_json)# json.dumps(efficiency_summary)

        #bmp_dict = {str(bmp.id): bmp.name for bmp in Bmp.objects.all()}
        #context['table3'] = ManureBmpCustomDataTable(manure)
        context['page_title'] = 'Proposed BMPs'
        context['solution_id'] = solution_id

               
        return context
    
    def get(self, request, *args, **kwargs):
        # Check if the request is an HTMX request
        if 'HX-Request' in request.headers and 'action' in request.GET:
            action = request.GET.get('action', 'nothing')
            print(action)

        else:
            return super().get(request, *args, **kwargs)

class DuplicateSolution(LoginRequiredMixin, TemplateView):
    template_name = 'solution/edit_solution.html'
    model =Solution 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        solution_id = self.kwargs.get('id')  # Assuming you're passing the ID in the URL

        solution = Solution.objects.get(id=solution_id)

        land_bmps = solution.land_json
        animal_bmps = solution.animal_json
        manure_bmps = solution.manure_json

        efficiency, efficiency_summary, animal, animal_summary, manure, manure_summary, costs, geo_jsons, lrs_geo_jsons  = get_bmps_by_sector(land_bmps, animal_bmps, manure_bmps)

        context['table'] = EfficiencyBmpCustomDataTable2(efficiency)
        context['table2'] = AnimalBmpCustomDataTable2(animal)
        #context['table3'] = ManureBmpCustomDataTable(manure)
        context['page_title'] = 'Edit BMPs'
        context['solution_id'] = solution_id

               
        return context

class DownloadSolution(LoginRequiredMixin, TemplateView):
    template_name = 'solution/download_solution.html'
    model =Solution 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        solution_id = self.kwargs.get('id')  # Assuming you're passing the ID in the URL

        solution = Solution.objects.get(id=solution_id)
        data = solution.data

        land_file = True if solution.land_json != {} else False
        animal_file = True if solution.animal_json != {} else False
        manure_file = True if solution.manure_json != {} else False

        selected_edge = 'EOS'
        loads = data['Loads']
        counter = 1
        loads_list = []
        for key, value in loads.items(): 
            row = value[selected_edge]
            row['id'] = counter
            row['sector'] = key
            loads_list.append(row)

            counter += 1
        context['table'] = SolutionBySectorTable(loads_list)
        context['solution_id'] = solution.id
        context['land_file'] = land_file
        context['animal_file'] = animal_file
        context['manure_file'] = manure_file
               
        return context

def read_csv_to_dict(filename, key_column, value_column):
    data_dict = {}
    
    with open(filename, 'r') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            key = row[key_column]
            value = row[value_column]
            data_dict[key] = value
    
    return data_dict
def read_dictionaries():
    prefix =  '/opt/opt4cast/csvs'
    agency_file = '{}/TblAgency.csv'.format(prefix)
    agency = read_csv_to_dict(agency_file, 'AgencyId', 'AgencyCode')
    state_file = '{}/TblState.csv'.format(prefix)
    state = read_csv_to_dict(state_file, 'StateId', 'StateAbbreviation')
    bmp_file = '{}/TblBmp.csv'.format(prefix)
    bmp = read_csv_to_dict(bmp_file, 'BmpId', 'BmpShortName')
    geography_file = '{}/TblGeography.csv'.format(prefix)
    geography = read_csv_to_dict(geography_file, 'GeographyId', 'GeographyName')
    load_src_grp_file = '{}/TblLoadSourceGroup.csv'.format(prefix)
    load_src_grp= read_csv_to_dict(load_src_grp_file, 'LoadSourceGroupId', 'LoadSourceGroup')
    animal_grp_file = '{}/TblAnimalGroup.csv'.format(prefix)
    animal_grp =  read_csv_to_dict(animal_grp_file, 'AnimalGroupId', 'AnimalGroup')
    unit_file = '{}/TblUnit.csv'.format(prefix)
    unit =  read_csv_to_dict(unit_file, 'UnitId', 'Unit')
    return agency, state, bmp, geography, load_src_grp, animal_grp, unit
        #path('generate_land_file/', views.generate_land_file, name='generate_land_file'),
        #path('generate_animal_file/', views.generate_animal_file, name='generate_animal_file'),
        #path('generate_manure_file/', views.generate_manure_file, name='generate_manure_file'),


@require_POST
def generate_land_file(request):
    if request.method == "POST" and request.headers.get('Hx-Request') == 'true':

        solution_id = request.POST.get('solution_id', None)
        solution = Solution.objects.get(id=solution_id)
        base_scenario = solution.execution.scenario.base_scenario
        df_land = pd.read_parquet(solution.land_file.path)
        base_content = {}

        if base_scenario.base_file:
            # Open the file in binary mode for reading
            with base_scenario.base_file.open('rb') as file:
                # Read the content of the file
                base_content = json.load(file)

        lrseg_dict_ = base_content['lrseg']
        u_u_group_dict_ = base_content['u_u_group']

        field_names = 'StateUniqueIdentifier	AgencyCode	StateAbbreviation	BmpShortname	GeographyName	LoadSourceGroup	Amount	Unit\r\n'
        # temporal filename will be deleted in one day
        out_filename = '/tmp/land_file_{}.txt'.format(solution_id)

        agency, state, bmp, geography_dict, load_src_grp, animal_grp, unit = read_dictionaries()
        
        with open(out_filename, 'w', newline='') as destination_file:
            destination_file.write(field_names)
            
            counter = 1
            for index, row in df_land.iterrows():
                agency_id = row['agency_id']
                curr_agency = agency[str(agency_id)]
                curr_state = (row['state']).lower()
                curr_bmp = bmp[str(row['bmp_id'])]
                lrs_id = row['lrs_id']
                fips, state, county, geography = lrseg_dict_[str(lrs_id)]
                curr_geo = geography_dict[str(geography)]
                load_src_grp_id = u_u_group_dict_[str(row['load_src_id'])] 
                curr_load_src_grp = load_src_grp[str(load_src_grp_id)] 
                destination_file.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\r\n'.format(counter, curr_agency, curr_state, curr_bmp, curr_geo, curr_load_src_grp, row['acres'], 'acres'))
                counter += 1
        file_url = request.build_absolute_uri(reverse('serve_temp_file', args=[solution_id]))
        return JsonResponse({'status': 'accept', 'message': 'File generated successfully.', 'file_url': file_url})

    else:
        # Handle non-POST request or non-HTMX request
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def serve_temp_file(request, solution_id):
    # Construct the file path using the solution_id
    file_path = '/tmp/land_file_{}.txt'.format(solution_id)
    
    # Make sure the file exists
    if not os.path.exists(file_path):
        raise Http404("File does not exist")

    # Serve the file
    response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
    return response

@require_POST
def generate_animal_file(request):
    if request.method == "POST" and request.headers.get('Hx-Request') == 'true':

        solution_id = request.POST.get('solution_id', None)
        solution = Solution.objects.get(id=solution_id)
        base_scenario = solution.execution.scenario.base_scenario
        df_animal = pd.read_parquet(solution.animal_file.path)
        base_content = {}

        if base_scenario.base_file:
            # Open the file in binary mode for reading
            with base_scenario.base_file.open('rb') as file:
                # Read the content of the file
                base_content = json.load(file)

        geography_county_ = base_content['counties']
        u_u_group_dict_ = base_content['u_u_group']


        field_names = 'StateUniqueIdentifier	AgencyCode	StateAbbreviation	BmpShortname	GeographyName	AnimalGroup	LoadSourceGroup	Amount	Unit	NReductionFraction	PReductionFraction\r\n'
        # temporal filename will be deleted in one day
        out_filename = '/tmp/animal_file_{}.txt'.format(solution_id)

        agency, state, bmp, geography_dict, load_src_grp, animal_grp, unit = read_dictionaries()

        
        with open(out_filename, 'w', newline='') as destination_file:
            destination_file.write(field_names)
            
            counter = 1
            for index, row in df_animal.iterrows():
                curr_agency = 'nonfed'
                curr_state = row['state']
                curr_bmp = bmp[str(row['bmp_id'])]
                county_id = str(row['county_id'])
                
                _, geography2_id, _, _, state_abbr = geography_county_[county_id]

                curr_geo = geography_dict[str(geography2_id)]
                src_grp_id = u_u_group_dict_[str(row['load_src_id'])] 
                curr_load_src_grp = load_src_grp[str(src_grp_id)]
                curr_animal_grp = row['animal']
                curr_unit = 'au' 

                destination_file.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t\t\r\n'.format(counter, curr_agency, curr_state, curr_bmp, curr_geo, curr_animal_grp, curr_load_src_grp, row['amount'], curr_unit))
                counter += 1
        file_url = request.build_absolute_uri(reverse('serve_temp_animal_file', args=[solution_id]))
        return JsonResponse({'status': 'accept', 'message': 'File generated successfully.', 'file_url': file_url})

    else:
        # Handle non-POST request or non-HTMX request
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def serve_temp_animal_file(request, solution_id):
    # Construct the file path using the solution_id
    file_path = '/tmp/animal_file_{}.txt'.format(solution_id)
    
    # Make sure the file exists
    if not os.path.exists(file_path):
        raise Http404("File does not exist")

    # Serve the file
    response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
    return response


@require_POST
def generate_manure_file(request):
    if request.method == "POST" and request.headers.get('Hx-Request') == 'true':

        solution_id = request.POST.get('solution_id', None)
        solution = Solution.objects.get(id=solution_id)
        base_scenario = solution.execution.scenario.base_scenario
        df_manure = pd.read_parquet(solution.manure_file.path)
        base_content = {}

        if base_scenario.base_file:
            # Open the file in binary mode for reading
            with base_scenario.base_file.open('rb') as file:
                # Read the content of the file
                base_content = json.load(file)

        geography_county_ = base_content['counties']
        u_u_group_dict_ = base_content['u_u_group']

        field_names = 'StateUniqueIdentifier	AgencyCode	StateAbbreviation	BmpShortName	FIPSFrom	FIPSTo	AnimalGroup	LoadSourceGroup	Amount	Unit\r\n'
        # temporal filename will be deleted in one day
        out_filename = '/tmp/manure_file_{}.txt'.format(solution_id)

        agency, state, bmp, geography_dict, load_src_grp, animal_grp, unit = read_dictionaries()
        
        with open(out_filename, 'w', newline='') as destination_file:
            destination_file.write(field_names)
            
            counter = 1
            for index, row in df_manure.iterrows():
                curr_agency = 'nonfed' 
                curr_state = (row['state']).lower()
                curr_bmp = bmp[str(row['bmp_id'])]
                county_from_id = str(row['county_from_id'])

                _, _, fips_from, _, _= geography_county_[county_from_id]

                county_to_id = str(row['county_to_id'])

                _, _, fips_to, _, _= geography_county_[county_to_id]

                load_src_grp_id = u_u_group_dict_[str(row['load_src_id'])] 
                curr_load_src_grp = load_src_grp[str(load_src_grp_id)] 
                curr_animal_grp = row['animal']

                destination_file.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\r\n'.format(counter, curr_agency, curr_state, curr_bmp, fips_from, fips_to, curr_animal_grp, curr_load_src_grp, row['amount'], 'wet tons'))
                counter += 1
        file_url = request.build_absolute_uri(reverse('serve_temp_manure_file', args=[solution_id]))
        return JsonResponse({'status': 'accept', 'message': 'File generated successfully.', 'file_url': file_url})

    else:
        # Handle non-POST request or non-HTMX request
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def serve_temp_manure_file(request, solution_id):
    # Construct the file path using the solution_id
    file_path = '/tmp/manure_file_{}.txt'.format(solution_id)
    
    # Make sure the file exists
    if not os.path.exists(file_path):
        raise Http404("File does not exist")

    # Serve the file
    response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
    return response


class DuplicateSolution2(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        solution_id = self.kwargs.get('id')
        original_solution = get_object_or_404(Solution, id=solution_id)

        new_solution = Solution.objects.create(
                execution = original_solution.execution, 
                data = original_solution.data, 
                info = original_solution.info, 
                added = True, 
                land_json = original_solution.land_json, 
                animal_json = original_solution.animal_json, 
                manure_json = original_solution.manure_json, 
        )
        # Duplicate the solution
        #solution.pk = None  # Reset the primary key to create a new instance
        # Modify any attributes as necessary, for example, mark it as not evaluated
        #solution.added = True
        #solution.save()

        # Redirect to an edit or detail view of the new solution
        return redirect(reverse('update_solution', kwargs={'id': new_solution.id}))
        # Replace 'solution_detail' with the name of your URL pattern for the detail or edit view


class UpdateSolution(LoginRequiredMixin, UpdateView):
    model = Solution 
    #form_class  = ScenarioForm
    template_name = 'solution/update_solution.html'
    context_object_name = 'object'
    pk_url_kwarg = 'id'  # This tells Django to use 'id' from the URL

    def get_success_url(self):
        return reverse('list_scenarios')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        solution_id = self.kwargs.get('id')  # Assuming you're passing the ID in the URL

        solution = Solution.objects.get(id=solution_id)

        land_bmps = solution.land_json
        animal_bmps = solution.animal_json
        manure_bmps = solution.manure_json
        efficiency, animal, manure, costs = get_bmps_by_sector(land_bmps, animal_bmps, manure_bmps)


        ctx['table'] = EfficiencyBmpCustomDataTable(efficiency)
        ctx['table2'] = AnimalBmpCustomDataTable(animal)
        ctx['page_title'] = 'Duplicate Solution'
        ctx['solution_id'] = solution_id
        ctx['next_step_url'] = 'step1'
        return ctx

@require_POST
@csrf_exempt  # Consider using CSRF tokens properly in production
def ChatResponse(request):
    data = json.loads(request.body)
    print(data)

    user_input = data.get('userInput', '')
    solution_id = data.get('solution_id', '')  # Retrieve the solution_id from the request

    solution = Solution.objects.get(id=solution_id)
    base_scenario = solution.execution.scenario.base_scenario
    df_base_reportloads = pd.read_parquet(base_scenario.reportloads_file.path)

    df_efficiency = pd.read_parquet(solution.land_file.path) if solution.land_file else pd.DataFrame()

    df_animal = pd.read_parquet(solution.animal_file.path) if solution.animal_file else pd.DataFrame()
    df_manure = pd.read_parquet(solution.manure_file.path) if solution.manure_file else pd.DataFrame()
    df_sector_loads = pd.read_parquet(solution.sector_loads_file.path) if solution.sector_loads_file else pd.DataFrame()

    # Create a pandas agent
    agent = create_pandas_dataframe_agent(OpenAI(temperature=0), [df_efficiency, df_sector_loads], verbose=False)
    
    # Interact with the DataFrame using natural language queries
    try:
        result = agent.invoke(user_input)
    except Exception as e:
        result = {'output': str(e)}

    #print(request.POST)
    #user_input = request.POST.get('user_input', '')
    # Process the input, e.g., querying an AI service or database
    response_text = f"EcoEcho: {result['output']}"  # Example response
    print(response_text)
    return JsonResponse({'content': f'<div>{response_text}</div>'})

