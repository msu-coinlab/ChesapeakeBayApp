from celery import shared_task
from io import BytesIO
from django.core.files.base import ContentFile
import time
from .models import * 
import os
import subprocess
from django.utils import timezone
import json
from django.core.files import File
import json
from django.db.models import Q
from uuid import uuid4
import pandas as pd
from os.path import basename

#from emails.models import Email, EmailTemplate
from zipfile import ZipFile
import zipfile

OPT4CAST_RUN_BASE_SIMPLE_PATH = os.environ.get('OPT4CAST_RUN_BASE_SIMPLE_PATH', '/home/gtoscano/projects/run_base/build/run_base_simple')
OPT4CAST_MAKE_SCENARIO_FILE_PATH = os.environ.get('OPT4CAST_MAKE_SCENARIO_FILE_PATH', '/home/gtoscano/projects/CastEvaluation/build/test/scenario_test')
OPT4CAST_RUN_EPS_CNSTR_PATH = os.environ.get('OPT4CAST_RUN_EPS_CNSTR_PATH', '/home/gtoscano/projects/MSUCast/build/eps_cnstr/eps_cnstr')
OPT4CAST_RUN_PSO_PATH = os.environ.get('OPT4CAST_RUN_PSO_PATH', '/home/gtoscano/projects/MSUCast/build/pso')
OPT4CAST_RUN_NSGA_PATH = os.environ.get('OPT4CAST_RUN_NSGA_PATH', '/home/gtoscano/projects/nsga3-cbw/build/nsga3-cbw')


@shared_task
def add(x, y):
    return x + y

def get_selected_bmps(selected_bmps):
    selected_bmps_set = set()  # Use a set to store unique values
    selected_bmps_list = []  # This will be the final list with unique values
    for _, values in selected_bmps.items():
        for value in values:
            if value not in selected_bmps_set:  # Check if the value is already added
                selected_bmps_set.add(value)  # Add the value to the set
                selected_bmps_list.append(value)  # Append the value to the list
    return selected_bmps_list

def get_all_file_paths(directory):
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            # join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

    # returning all file paths
    return file_paths

def zip_directory(directory_path, zip_path, prefix='/results/' ):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, directory_path)
                zipf.write(file_path, prefix + arcname)

def zipit(directory, zip_filename, prefix='/results/'):
    file_paths = get_all_file_paths(directory)
    # writing files to a zipfile
    with ZipFile(zip_filename,'w') as zip:
        # writing each file one by one
        for file in file_paths:
            zip.write(file, prefix + basename(file))

@shared_task
def send_base_scenarios():

    #initialize_globals()
    #failed_scenarios = BaseScenario.objects.filter(status=BaseScenario.STATUS_FAILED)
    failed_or_pending_scenarios = BaseScenario.objects.filter(status='F')
    
    for scenario in failed_or_pending_scenarios:
        BaseScenario.objects.filter(pk=scenario.id).update(status='E', uuid=uuid4())
        process_new_base_scenario(scenario.id)

def get_selected_states(areas):
        all_states_dict =  {state.abbreviation: state.id for state in State.objects.all()}
        states_list = []
        for area in areas:
            state = all_states_dict[area.state.lower()]
            if state not in states_list:
                states_list.append(state);
        return states_list;

def run_base_scenario(base_scenario_id):
    BaseScenario.objects.filter(pk=base_scenario_id).update(status='E')
    base_scenario = BaseScenario.objects.get(id=base_scenario_id)
    uuid = base_scenario.uuid
    sinfo = ScenarioInfo.objects.get(pk=base_scenario.scenario_info.id)
    geographic_areas = base_scenario.geographic_areas.all()
    geographic_area_list = [] 
    for geographic_area in geographic_areas:
        geographic_area_list.append(geographic_area.id)
    geography = '_'.join(str(geo) for geo in geographic_area_list)
    scenario_name = 'base' 
    historical_crop_need_scenario= 6608
    ncounties = len(geographic_area_list)
    emo_data = "{}_{}_{}_{}_{}_{}_{}_{}_{}_{}_{}_{}_{}_{}".format(
            scenario_name, 
            sinfo.atm_dep, 
            sinfo.backout, 
            sinfo.condition, 
            sinfo.base_load, 
            4, 
            sinfo.climate_change, 
            ncounties, 
            historical_crop_need_scenario, 
            sinfo.point_src, 
            sinfo.type_id, 
            sinfo.soil, 
            sinfo.data_revision, 
            geography)

    args = [OPT4CAST_RUN_BASE_SIMPLE_PATH, emo_data, str(uuid), str(ncounties) ]
    print(args)

    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    print(stdout)
    print(stderr)

    stdout_str = stdout.decode('utf-8')
    stderr_str = stderr.decode('utf-8')
    
    # Check the process exit status
    if process.returncode == 0:
        print("Process completed successfully")
    else:
        print("Process failed")
    if len(stderr_str) > 0:
        print('Error in make_scenario_file: First')
        print(stderr_str)
        #BaseScenario.objects.filter(pk=base_scenario_id).update(status='F', error=stderr)
        #return

    #print ("stdout", stdout_str)
    #print ("err", stderr)
    #print('SINFO.ID', sinfo.id)



def make_base_scenario_init_file(base_scenario_id):
    print("Inside make_base_scenario_init_file")
    BaseScenario.objects.filter(pk=base_scenario_id).update(status='E')
    base_scenario = BaseScenario.objects.get(id=base_scenario_id)
    uuid = base_scenario.uuid

    sinfo = ScenarioInfo.objects.get(pk=base_scenario.scenario_info.id)
    report_loads_path= f'/opt/opt4cast/output/nsga3/{uuid}/config/reportloads.csv'
    report_loads_parquet_path= f'/opt/opt4cast/output/nsga3/{uuid}/config/reportloads.parquet'
    manure_nutrients_parquet_path= f'/opt/opt4cast/output/nsga3/{uuid}/config/manurenutrientsconfinement.parquet'
    output_json_path = f'/opt/opt4cast/output/nsga3/{uuid}/config/reportloads_processed.json'
    args = [OPT4CAST_MAKE_SCENARIO_FILE_PATH, str(sinfo.id), report_loads_path, output_json_path] 
    print(' '.join(args))
    process2 = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout, stderr = process2.communicate()

    stdout_str = stdout.decode('utf-8')
    stderr_str = stderr.decode('utf-8')
    
    # Check the process exit status
    if process2.returncode == 0:
        print("Process completed successfully")
    else:
        print("Process failed")
    if len(stderr) > 0:
        print('Error in make_scenario_file')
        print(stderr)
        #BaseScenario.objects.filter(pk=base_scenario_id).update(status='F', error=stderr)
        #return

    with open(output_json_path, 'r') as file:
        output_data = json.load(file)

    sum_load_invalid = output_data.get('sum_load_invalid', [])
    sum_load_valid = output_data.get('sum_load_valid', [])
    total_loads = [invalid + valid for invalid, valid in zip(sum_load_invalid, sum_load_valid)]

    amount_dict = output_data.get('amount', {})
    total_amount = sum(amount_dict.values())
    store_json = {}
    store_json['sum_load_invalid'] = output_data['sum_load_invalid'] 
    store_json['sum_load_valid'] = output_data['sum_load_valid']
    store_json['sum_load_total'] = total_loads 
    store_json['amount'] = output_data['amount']
    store_json['total_amount'] = total_amount
    store_json['states'] = get_selected_states(base_scenario.geographic_areas.all()) 


    with open(output_json_path, 'rb') as f:
        out_file = File(f, f'reportloads.json')
        # Update the fields
        base_scenario.base_file.save(out_file.name, out_file, save=False)

    with open(report_loads_parquet_path, 'rb') as f:
        out_file = File(f, f'reportloads.parquet')
        # Update the fields
        base_scenario.reportloads_file.save(out_file.name, out_file, save=False)

    with open(manure_nutrients_parquet_path, 'rb') as f:
        out_file = File(f, f'manurenutrientsconfinement.parquet')
        # Update the fields
        base_scenario.manure_nutrients_file.save(out_file.name, out_file, save=False)
    
    base_scenario.status = 'C'
    base_scenario.completed = timezone.now()
    base_scenario.data = store_json
    # Save the instance
    base_scenario.save()
    #BaseScenario.objects.filter(pk=base_scenario_id).update(status='C', completed=timezone.now(), data=json.dumps(store_json), base_file=out_file) 
    #basefile = BaseFile(base_id=data['id'], base_file=out_file)
    #basefile.save()


    Scenario.objects.filter(status='P',base_scenario=base_scenario_id).update(status='C')

@shared_task
def process_new_base_scenario(base_scenario_id):
    #initialize_globals()
    run_base_scenario(base_scenario_id)
    print("Running Base Scenario Done")
    make_base_scenario_init_file(base_scenario_id)
    print("Running Base Scenario Init File Done")

@shared_task
def process_new_optimization(scenario_id):
    #initialize_globals()
    uuid=uuid4()
    niterations = 20 
    print('inside of process new optimization: ', uuid)
    path = f'/opt/opt4cast/output/nsga3/{uuid}/config'
    print(path)
    if not os.path.exists(path):
        os.makedirs(path)

    scenario = Scenario.objects.get(id=scenario_id)
    bmps = scenario.bmps
    #selected_bmps = bmps['selected_bmps']

    selected_bmps = get_selected_bmps(bmps['target_items'])
    costs = scenario.costs
    bmp_cost_dict = {}
    for key, value in costs.items():
        bmp_cost = BmpCost.objects.get(id=int(key))
        bmp_cost_dict[f'{bmp_cost.state.id}_{bmp_cost.bmp.id}'] = value['new_cost']
    loads = scenario.loads
    manure_counties = []
    if 'target_items' in scenario.manure_counties.keys():
        manure_counties = scenario.manure_counties['target_items']

    scenario_dict = {}
    scenario_dict['selected_bmps'] = selected_bmps
    scenario_dict['bmp_cost'] = bmp_cost_dict
    scenario_dict['selected_pollutant'] = loads['selected_pollutant']

    if 'total_budget' in loads.keys():
        scenario_dict['total_budget'] = loads['total_budget']
    pollutant_to_idx = {'nitrogen': 0, 'phosphorus': 1, 'sediments': 2, 'oxygen': 3}
    greatest_reduction = ''
    for idx, val in enumerate(loads['selected_pollutant']):
        if idx ==0:
            greatest_reduction = val 
        elif loads[f'{val}_pct'] > loads[f'{greatest_reduction}_pct']:
            greatest_reduction = val

    sel_pollutant = pollutant_to_idx[greatest_reduction]
    target_pct = 1.0 - (loads[f'{greatest_reduction}_pct']/100.0)
    selected_dict = {'EOS': 0, 'EOR': 1, 'EOT': 2, 'Oxygen': 3}

    selected_reduction_target = selected_dict[loads['selected_reduction_target']]
    scenario_dict['selected_reduction_target'] = selected_reduction_target 
    scenario_dict['nitrogen_pct'] = loads['nitrogen_pct']
    scenario_dict['phosphorus_pct'] = loads['phosphorus_pct']
    scenario_dict['sediments_pct'] = loads['sediments_pct']
    scenario_dict['oxygen_pct'] = loads['oxygen_pct']
    scenario_dict['target_pct'] = target_pct
    scenario_dict['sel_pollutant'] = sel_pollutant
    scenario_dict['niterations'] = niterations
    scenario_dict['manure_counties'] = manure_counties

    scenario_dict['uuid'] = str(uuid)
    # save scenario_dict to a json file

    reportloads_json_path = f'{path}/reportloads_processed.json'
    scenario_json_path = f'{path}/scenario.json'
    manure_nutrients_path = f'{path}/manurenutrientsconfinement.parquet'
    pfront_path = f'/opt/opt4cast/output/nsga3/{uuid}/front'

    if not os.path.exists(pfront_path):
        os.makedirs(pfront_path)

    # Check if base_file exists
    if scenario.base_scenario.manure_nutrients_file:
        # Open the file in binary mode for reading
        with scenario.base_scenario.manure_nutrients_file.open('rb') as file:
            # Read the content of the file
            manure_nutrients_file_content = file.read()
        
        # Write the content to the specified file
        with open(manure_nutrients_path, 'wb') as destination_file:
            destination_file.write(manure_nutrients_file_content)

    if scenario.base_scenario.base_file:
        # Open the file in binary mode for reading
        with scenario.base_scenario.base_file.open('rb') as file:
            # Read the content of the file
            file_content = file.read()
        
        # Write the content to the specified file
        with open(reportloads_json_path, 'wb') as destination_file:
            destination_file.write(file_content)
    else:
        # Handle the case when base_file is None
        print('Base file does not exist')


    print('scenario_dict', scenario_dict)
    with open(scenario_json_path, 'w') as json_file:
        json.dump(scenario_dict, json_file)
    
    # BmpType=5 (Animal Manure) 35 , 69 , 71 , 135 , 203 , 204 , 205 , 206
            # BmpCategoryId=2 35 , 69 , 71 , 135 , 203 , 204 , 205 , 206
            # Manure Transport = 31
    
    lc_bmp_list = [2, 7, 8, 9, 11, 12, 13, 14, 15, 17, 18, 19, 21, 22, 61, 62, 65, 66, 120, 140, 200, 207, 275, 276, 277, 278, 279, 280]
    any_lc_bmp = any(item in lc_bmp_list for item in selected_bmps)

    print('Selected_bmps', selected_bmps)
    animal_bmp_list = [35, 69, 71, 135, 203, 204, 205]
    any_animal_bmp = any(item in animal_bmp_list for item in selected_bmps)
    print('Any Animal BMP', any_animal_bmp)
    manure_transport_bmp_list  = [31]
    any_manure_transport_bmp = any(item in manure_transport_bmp_list for item in selected_bmps)
    print('Any Manure Transport', any_manure_transport_bmp)


    if any_lc_bmp or any_animal_bmp:# or any_manure_transport_bmp:
        lc_bmps = 0
        efficiency_bmps = 1
        animal_bmps = 0
        manure_transport_bmps = 0
        if any_lc_bmp:
            lc_bmps = 1
        if any_animal_bmp:
            animal_bmps = 1
        if any_manure_transport_bmp:
            manure_transport_bmps = 0

        args = [OPT4CAST_RUN_PSO_PATH, reportloads_json_path, scenario_json_path,  pfront_path, str(efficiency_bmps), str(lc_bmps), str(animal_bmps), str(manure_transport_bmps), manure_nutrients_path]
        #./pso /home/gtoscano/projects/MSUCast/build/reportloads_processed.json /home/gtoscano/projects/MSUCast/build/scenario.json ./test2 1 1 1 0

        print(" ".join(args))
        #return
    else:
    
        args = [OPT4CAST_RUN_EPS_CNSTR_PATH, reportloads_json_path, scenario_json_path, pfront_path, str(sel_pollutant), str(target_pct), str(niterations)]
        print('run cnstr')
        print(" ".join(args))

    process3 = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process3.communicate()
    stdout_str = stdout.decode('utf-8')
    stderr_str = stderr.decode('utf-8')
    
    # Check the process exit status
    if process3.returncode == 0:
        print("Process completed successfully")
    else:
        print("Process failed")
        print(stderr_str)
        print(stdout_str) 

    execution = Execution.objects.create(uuid=uuid, scenario=scenario, loads=scenario.loads, bmps=bmps, costs=scenario.costs, bmp_constraints=scenario.bmp_constraints, advanced_constraints=scenario.advanced_constraints)
    execution.save()

    print(execution.id)

    prefix = 'front'
    config_path = f'/opt/opt4cast/output/nsga3/{uuid}'

    retrieve_optimization_solutions(execution.id, prefix, config_path)

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
            # Read each line, split by comma, and get the first value
            first_values = [row.split(',')[0] for row in file if row.strip()]
        return first_values
    except FileNotFoundError:
        return "File not found."

def load_json_data(file_path):
    try:
        with open(file_path, 'r') as file:
            # Read each line, split by comma, and get the first value
            data = json.load(file)
            return data
        return first_values
    except FileNotFoundError:
        return "File not found."

def compute_costs(submitted_land):
    total_cost = 0.0
    for key, value in submitted_land.items():
        lrs_id , agency, load_src, bmp = key.split('_')
        lrs = LandRiverSegment.objects.filter(id=int(lrs_id)).get()
        state = lrs.state.id
        cost = BmpCost.objects.filter(Q(bmp_state=r'{bmp}_{state}')).get()
        total_cost += cost * value

    return total_cost

def get_land_bmps_by_sector_lrs(land_bmps):
        counter = 1
        efficiency = []
        costs = {}
        lrs_geo_jsons = {}
        for key, value in land_bmps.items():
            result_list = key.split("_")
            lrs = result_list[0]
            agency_id = result_list[1]
            #agency_dict = {str(agency.id): agency.name for agency in Agency.objects.all()}
            #agency = agency_dict[agency_id]
            agency = Agency.objects.get(id=agency_id).name
            load_id = result_list[2]

            #load_src_dict = {str(load_src.id): load_src.name for load_src in LoadSrc.objects.all()}
            #load_src = load_src_dict[load_id]
            load_src = LoadSrc.objects.get(id=load_id).name
            #sector = load_src_sector_dict[result_list[2]]
            sector = LoadSrc.objects.get(id=result_list[2]).sector.name
            bmp_id = result_list[3]

            #bmp_dict = {str(bmp.id): bmp.name for bmp in Bmp.objects.all()}
            #bmp = bmp_dict[bmp_id]
            bmp = Bmp.objects.get(id=bmp_id).name
            lrs_item =  LandRiverSegment.objects.get(id=lrs)
            state_abbr = lrs_item.geographic_area.state
            state_id = State.objects.get(abbreviation=state_abbr.lower()).id
            price = float(BmpCost.objects.filter(Q(state__id=state_id), Q(bmp__id=bmp_id)).first().cost)
            cost = price * value

            efficiency.append({'state_id': int(state_id), 'state': state_abbr, 'county_id': lrs_item.geographic_area.id, 'county': lrs_item.geographic_area.name,  'lrs_id': int(lrs), 'lrs': LandRiverSegment.objects.get(id=lrs).name, 'agency_id': int(agency_id), 'agency': agency,  'load_src_id': int(load_id), 'load_src': load_src, 'sector': sector, 'bmp_id': int(bmp_id), 'bmp': bmp, 'acres': value, 'price': price, 'cost': cost})

        df = pd.DataFrame(efficiency)
        df['state_id'] = df['state_id'].astype('Int8')  # Use 'Int32', 'Int16', or 'Int8' as needed
        df['county_id'] = df['county_id'].astype('Int16')  # Use 'Int32', 'Int16', or 'Int8' as needed
        df['lrs_id'] = df['lrs_id'].astype('Int16')
        df['agency_id'] = df['agency_id'].astype('Int8')
        df['load_src_id'] = df['load_src_id'].astype('Int8')
        df['bmp_id'] = df['bmp_id'].astype('Int16')
        df['acres'] = df['acres'].astype('float32')
        df['price'] = df['price'].astype('float32')
        df['cost'] = df['cost'].astype('float32')
        return df


def get_animal_bmps_by_sector_lrs(animal_bmps):

        counter = 1
        animal = [] 
        for key, value in animal_bmps.items():
            result_list = key.split("_")
            base_condition= result_list[0]
            county_id = result_list[1]
            county_item = GeographicArea.objects.get(county=county_id)
            county = county_item.name
            state_abbr = county_item.state 
            state_id = State.objects.get(abbreviation=state_abbr.lower()).id
            #county2 = county_dict[result_list[1]]
            #print(county2)
            load_src_id = result_list[2]
            #load_src = load_src_dict[load_src_id]
            load_src = LoadSrc.objects.get(id=load_src_id).name
            #sector = load_src_sector_dict[load_src_id]
            sector = LoadSrc.objects.get(id=load_src_id).sector.name
            animal_id = result_list[3]
            #animal_name = animal_dict[animal_id]
            animal_name = AnimalGrp.objects.get(id=animal_id).name
            bmp_id = result_list[4]
            #bmp = bmp_dict[bmp_id]

            bmp = Bmp.objects.get(id=bmp_id).name
            price = float(BmpCost.objects.filter(Q(state__id=state_id), Q(bmp__id=bmp_id)).first().cost)
            cost = price * value
            animal.append({'id': counter, 'base_condition': base_condition, 'state_id': state_id, 'state': state_abbr ,'county_id': county_id, 'county': county, 'load_src_id': load_src_id, 'load_src': load_src, 'sector': sector, 'animal_id': animal_id, 'animal': animal_name, 'bmp_id': bmp_id, 'bmp': bmp, 'amount': value, 'price': price, 'cost': cost})


        df = pd.DataFrame(animal)
        df['state_id'] = df['state_id'].astype('Int8')  # Use 'Int32', 'Int16', or 'Int8' as needed
        df['county_id'] = df['county_id'].astype('Int16')  # Use 'Int32', 'Int16', or 'Int8' as needed
        df['load_src_id'] = df['load_src_id'].astype('Int8')
        df['animal_id'] = df['animal_id'].astype('Int8')
        df['bmp_id'] = df['bmp_id'].astype('Int16')
        df['price'] = df['price'].astype('float32')
        df['cost'] = df['cost'].astype('float32')
        return df

def get_manure_bmps_by_sector_lrs(manure_bmps):
        counter = 1
        manure = [] 
        for key, value in manure_bmps.items():
            result_list = key.split("_")
            county_from_id = result_list[0]
            county_to_id = result_list[1]
            load_src_id = result_list[2]
            animal_id = result_list[3]
            bmp_id = result_list[4]

            county_from_item = GeographicArea.objects.get(county=county_from_id)
            county_to_item = GeographicArea.objects.get(county=county_to_id)
            county_from = county_from_item.name
            county_to = county_to_item.name
            state_abbr = county_from_item.state 
            state_id = State.objects.get(abbreviation=state_abbr.lower()).id
            #county2 = county_dict[result_list[1]]
            #print(county2)
            #load_src = load_src_dict[load_src_id]
            load_src = LoadSrc.objects.get(id=load_src_id).name
            #sector = load_src_sector_dict[load_src_id]
            sector = LoadSrc.objects.get(id=load_src_id).sector.name

            #animal_name = animal_dict[animal_id]
            animal_name = AnimalGrp.objects.get(id=animal_id).name
            #bmp = bmp_dict[bmp_id]
            bmp = Bmp.objects.get(id=bmp_id).name
            price = float(BmpCost.objects.filter(Q(state__id=state_id), Q(bmp__id=bmp_id)).first().cost)
            cost = price * value
            manure.append({'id': counter, 'state_id': state_id, 'state': state_abbr, 'county_from_id': county_from_id, 'county_from': county_from, 'county_to_id': county_to_id,  'county_to': county_to, 'load_src_id': load_src_id, 'load_src': load_src, 'sector': sector, 'animal_id': animal_id, 'animal': animal_name, 'bmp_id': bmp_id, 'bmp': bmp, 'amount': value, 'price': price, 'cost': cost})


        df = pd.DataFrame(manure)
        df['state_id'] = df['state_id'].astype('Int8')  # Use 'Int32', 'Int16', or 'Int8' as needed
        df['county_from_id'] = df['county_from_id'].astype('Int16')  # Use 'Int32', 'Int16', or 'Int8' as needed
        df['county_to_id'] = df['county_to_id'].astype('Int16')  # Use 'Int32', 'Int16', or 'Int8' as needed
        df['load_src_id'] = df['load_src_id'].astype('Int8')
        df['animal_id'] = df['animal_id'].astype('Int8')
        df['bmp_id'] = df['bmp_id'].astype('Int16')
        df['price'] = df['price'].astype('float32')
        df['cost'] = df['cost'].astype('float32')
        return df


def get_loads_by_sector(df_reportloads, df_base_reportloads):
        columns_to_sum = ['Amount', 'NLoadEos', 'PLoadEos', 'SLoadEos', 'NLoadEor', 'PLoadEor', 'SLoadEor', 'NLoadEot', 'PLoadEot', 'SLoadEot']

        loads_by_lrseg_and_sector = df_reportloads.groupby(['LrsegId', 'SectorId'])[columns_to_sum].sum().reset_index()
        base_loads_by_lrseg_and_sector = df_base_reportloads.groupby(['LrsegId', 'SectorId'])[columns_to_sum].sum().reset_index()

        loads_by_lrseg_and_sector_list = loads_by_lrseg_and_sector.to_dict(orient='records')
        base_loads_by_lrseg_and_sector_list = base_loads_by_lrseg_and_sector.to_dict(orient='records')
        loads_list = [] 
        for row in loads_by_lrseg_and_sector_list:
            lrs = LandRiverSegment.objects.get(id=row['LrsegId'])
            new_row = {
                'state_id': lrs.state.id,
                'state': lrs.state.abbreviation.upper(),
                'county_id': lrs.geographic_area.id,
                'county': lrs.geographic_area.name,
                'sector_id': row['SectorId'],
                'sector': Sector.objects.get(id=row['SectorId']).name,
                'lrs_id': lrs.id,
                'lrs': lrs.name,
                'amount': round(row['Amount'], 2),
                'Ns': round(row['NLoadEos'], 2),
                'Ps': round(row['PLoadEos'], 2),
                'Ss': round(row['SLoadEos'], 2),
                'Nr': round(row['NLoadEor'], 2),
                'Pr': round(row['PLoadEor'], 2),
                'Sr': round(row['SLoadEor'], 2),
                'Nt': round(row['NLoadEot'], 2),
                'Pt': round(row['PLoadEot'], 2),
                'St': round(row['SLoadEot'], 2)
            }
            if new_row['Ns'] + new_row['Ps'] + new_row['Ss'] + new_row['Nr'] + new_row['Pr'] + new_row['Sr'] + new_row['Nt'] + new_row['Pt'] + new_row['St'] > 0.0:
                loads_list.append(new_row)
        # Processing base loads
        Bloads_list = []
        for row in base_loads_by_lrseg_and_sector_list:
            # Find the matching row in loads_list to update
            # Assuming LrsegId and SectorId uniquely identify a row in loads_list
            matching_rows = [l for l in loads_list if l['lrs_id'] == row['LrsegId'] and l['sector_id'] == row['SectorId']]
            if matching_rows:
                # Update the existing row with base loads information
                matching_row = matching_rows[0]
                matching_row['Bamount'] = round(row['Amount'], 2)
                matching_row['BNs'] = round(row['NLoadEos'], 2)
                matching_row['BPs'] = round(row['PLoadEos'], 2)
                matching_row['BSs'] = round(row['SLoadEos'], 2)
                matching_row['BNr'] = round(row['NLoadEor'], 2)
                matching_row['BPr'] = round(row['PLoadEor'], 2)
                matching_row['BSr'] = round(row['SLoadEor'], 2)
                matching_row['BNt'] = round(row['NLoadEot'], 2)
                matching_row['BPt'] = round(row['PLoadEot'], 2)
                matching_row['BSt'] = round(row['SLoadEot'], 2)
            else:
                lrs = LandRiverSegment.objects.get(id=row['LrsegId'])
                new_row = {
                    'state_id': lrs.state.id,
                    'state': lrs.state.abbreviation.upper(),
                    'county_id': lrs.geographic_area.id,
                    'county': lrs.geographic_area.name,
                    'sector_id': row['SectorId'],
                    'sector': Sector.objects.get(id=row['SectorId']).name,
                    'lrs_id': lrs.id,
                    'lrs': lrs.name,
                    'amount': 0.0,
                    'Ns': 0.0,
                    'Ps': 0.0,
                    'Ss': 0.0,
                    'Nr': 0.0,
                    'Pr': 0.0,
                    'Sr': 0.0,
                    'Nt': 0.0,
                    'Pt': 0.0,
                    'St': 0.0,
                    'Bamount': round(row['Amount'], 2),
                    'BNs': round(row['NLoadEos'], 2),
                    'BPs': round(row['PLoadEos'], 2),
                    'BSs': round(row['SLoadEos'], 2),
                    'BNr': round(row['NLoadEor'], 2),
                    'BPr': round(row['PLoadEor'], 2),
                    'BSr': round(row['SLoadEor'], 2),
                    'BNt': round(row['NLoadEot'], 2),
                    'BPt': round(row['PLoadEot'], 2),
                    'BSt': round(row['SLoadEot'], 2),
                }
                if new_row['Ns'] + new_row['Ps'] + new_row['Ss'] + new_row['Nr'] + new_row['Pr'] + new_row['Sr'] + new_row['Nt'] + new_row['Pt'] + new_row['St'] > 0.0:
                    Bloads_list.append(new_row)
        loads_list.extend(Bloads_list)
        df_loads = pd.DataFrame(loads_list)
        df_loads['state_id'] = df_loads['state_id'].astype('Int8')  # Use 'Int32', 'Int16', or 'Int8' as needed
        df_loads['county_id'] = df_loads['county_id'].astype('Int16')  # Use 'Int32', 'Int16', or 'Int8' as needed
        df_loads['lrs_id'] = df_loads['lrs_id'].astype('Int16')
        df_loads['sector_id'] = df_loads['sector_id'].astype('Int8')
        df_loads['amount'] = df_loads['amount'].astype('float32')
        df_loads['Ns'] = df_loads['Ns'].astype('float32')
        df_loads['Ps'] = df_loads['Ps'].astype('float32')
        df_loads['Ss'] = df_loads['Ss'].astype('float32')
        df_loads['Nr'] = df_loads['Nr'].astype('float32')
        df_loads['Pr'] = df_loads['Pr'].astype('float32')
        df_loads['Sr'] = df_loads['Sr'].astype('float32')
        df_loads['Nt'] = df_loads['Nt'].astype('float32')
        df_loads['Pt'] = df_loads['Pt'].astype('float32')
        df_loads['St'] = df_loads['St'].astype('float32')
        df_loads['Bamount'] = df_loads['Bamount'].astype('float32')
        df_loads['BNs'] = df_loads['BNs'].astype('float32')
        df_loads['BPs'] = df_loads['BPs'].astype('float32')
        df_loads['BSs'] = df_loads['BSs'].astype('float32')
        df_loads['BNr'] = df_loads['BNr'].astype('float32')
        df_loads['BPr'] = df_loads['BPr'].astype('float32')
        df_loads['BSr'] = df_loads['BSr'].astype('float32')
        df_loads['BNt'] = df_loads['BNt'].astype('float32')
        df_loads['BPt'] = df_loads['BPt'].astype('float32')
        df_loads['BSt'] = df_loads['BSt'].astype('float32')
        return df_loads

def retrieve_optimization_solutions(execution_id, prefix, config_path):
    #from core.tasks import load_json_data, get_loads_by_sector, get_land_bmps_by_sector_lrs, get_animal_bmps_by_sector_lrs, get_manure_bmps_by_sector_lrs
    from io import BytesIO
    from django.core.files.base import ContentFile
    from django.core.files import File

    #execution_id = 34
    #prefix = 'front'
    #config_path = '/home/gtoscano/projects/CastPSO/build/lancaster_lc_an_manure'
    execution = Execution.objects.get(id=execution_id)
    scenario = execution.scenario
    base_scenario = scenario.base_scenario

    results_path = f'{config_path}/{prefix}/pareto_front.txt'
    #counter = count_rows_in_file(pfront)

    costs = get_first_values_from_file(results_path)
    nsolutions = len(costs)
    print('nsolutions', nsolutions)
    submitted_land = {}
    submitted_animal = {}
    submitted_manuretransport = {}

    for i in range(nsolutions):
        submmited_land_path = f'{config_path}/{prefix}/{i}_impbmpsubmittedland.json'
        if os.path.exists(submmited_land_path):
            submitted_land = load_json_data(submmited_land_path)

        submitted_animal_path = f'{config_path}/{prefix}/{i}_impbmpsubmittedanimal.json'
        if os.path.exists(submitted_animal_path):
            submitted_animal = load_json_data(submitted_animal_path)

        submitted_manuretransport_path = f'{config_path}/{prefix}/{i}_impbmpsubmittedmanuretransport.json'
        if os.path.exists(submitted_manuretransport_path):
            submitted_manuretransport = load_json_data(submitted_manuretransport_path)

        reportloads_path = f'{config_path}/{prefix}/{i}_reportloads.parquet'


        #['NLoadEos','PLoadEos','SLoadEos','NLoadEor','PLoadEor','SLoadEor','NLoadEot','PLoadEot','SLoadEot']
        df = pd.read_parquet(reportloads_path)
        df_base_reportloads = pd.read_parquet(base_scenario.reportloads_file.path)
        df_loads_by_sector = get_loads_by_sector(df, df_base_reportloads)
        #df_loads_by_sector = get_loads_by_sector(df)
        
        # Columns to sum
        columns_to_sum = ['NLoadEos', 'PLoadEos', 'SLoadEos', 'NLoadEor', 'PLoadEor', 'SLoadEor', 'NLoadEot', 'PLoadEot', 'SLoadEot']

        # Grouping by 'SectorId' and summing the specified columns for each group
        loads_by_sector = df.groupby('SectorId')[columns_to_sum].sum().reset_index()
        
        # Summing the specified columns
        total_sum_by_columns = df[columns_to_sum].sum()
        objectives = [costs[i]] + total_sum_by_columns.tolist()

        if objectives[1] > 22500000:
            print('lower than: ', objectives[0], objectives[1])
        else:
            print('greater than: ', objectives[0], objectives[1])

        total = {'Cost': float(objectives[0]), 'EOS': {'N': float(objectives[1]), 'P': float(objectives[2]), 'S': float(objectives[3])}, 'EOR': {'N': float(objectives[4]), 'P': float(objectives[5]), 'S': float(objectives[6])}, 'EOT': {'N': float(objectives[7]), 'P': float(objectives[8]), 'S': float(objectives[9])}} 

        #sector_dict = {str(sector.id): f'{sector.name}' for sector in Sector.objects.all()}
        sector_names = [sector.name for sector in Sector.objects.all()]
        loads_dict = {}

        for index, loads in loads_by_sector.iterrows():
            #sector_name = sector_dict[str(int(loads['SectorId']))]
            sector_name = Sector.objects.get(id=int(loads['SectorId'])).name
            loads_dict[sector_name]  = {'Cost': float(0.0), 'EOS': {'N': float(loads['NLoadEos']), 'P': float(loads['PLoadEos']), 'S': float(loads['SLoadEos'])}, 'EOR': {'N': float(loads['NLoadEor']), 'P': float(loads['PLoadEor']), 'S': float(loads['SLoadEor'])}, 'EOT': {'N': float(loads['NLoadEot']), 'P': float(loads['PLoadEot']), 'S': float(loads['SLoadEot'])}}
        loads_dict['Total'] = total

        data = {'Loads': loads_dict, 'sector_names': sector_names}


        #content_land = ContentFile(output.getvalue(), name="land_file.parquet")
        
        # Create a Django File object from this binary output
        solution = Solution.objects.create(execution=execution, land_json= submitted_land, animal_json=submitted_animal, manure_json=submitted_manuretransport, data=data) 
        if submitted_land != {}:
            df_land = get_land_bmps_by_sector_lrs(submitted_land)
            output = BytesIO()
            df_land.to_parquet(output, index=False)
            output.seek(0)  # Important: Rewind to the start of the BytesIO object
            content_land = ContentFile(output.getvalue(), name="land_file.parquet")
            solution.land_file.save(content_land.name, content_land, save=False)
        if submitted_animal != {}:
            df_animal = get_animal_bmps_by_sector_lrs(submitted_animal)
            output = BytesIO()
            df_animal.to_parquet(output, index=False)
            output.seek(0)  # Important: Rewind to the start of the BytesIO object
            content_animal = ContentFile(output.getvalue(), name="animal_file.parquet")
            solution.animal_file.save(content_animal.name, content_animal, save=False)
        if submitted_manuretransport != {}:
            df_manure = get_manure_bmps_by_sector_lrs(submitted_manuretransport)
            output = BytesIO()
            df_manure.to_parquet(output, index=False)
            output.seek(0)  # Important: Rewind to the start of the BytesIO object
            content_manure = ContentFile(output.getvalue(), name="manure_file.parquet")
            solution.manure_file.save(content_manure.name, content_manure, save=False)

        with open (reportloads_path, 'rb') as f:
            out_file = File(f, name=f'reportloads.parquet')
            solution.reportloads_file.save(out_file.name, out_file, save=False)

        output = BytesIO()
        df_loads_by_sector.to_parquet(output, index=False)
        output.seek(0)
        content_sector_loads = ContentFile(output.getvalue(), name="sector_loads_file.parquet")
        solution.sector_loads_file.save(content_sector_loads.name, content_sector_loads, save=False)
        solution.save()