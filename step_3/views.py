from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import ScenarioInfo, Scenario, BaseScenario, Execution
from core.models import BmpCategory, Bmp, BmpType, Sector
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json


def get_selected_bmps(selected_bmps):
        selected_bmps_list = []
        for _, value in selected_bmps.items():
            if value not in selected_bmps_list:
                selected_bmps_list.extend(value)
        return selected_bmps_list

def get_bmps_in_dict(data):
    items_dict = {}
    for category in data:
        category_dict = json.loads(category)
        category_label = category_dict['label']
        items = [int(item) for item in category_dict['items']]
        items_dict[category_label] = items
    return items_dict


@require_POST
def update_selected_bmps(request):
    data = request.POST
    try:
        source_items = data.getlist('sourceItems')
        target_items = data.getlist('targetItems')
        scenario_id = data.get('scenario_id')
        scenario_id = int(scenario_id)
        source_dict = {} if source_items is None else get_bmps_in_dict(source_items)
        target_dict = {} if target_items is None else get_bmps_in_dict(target_items)
        scenario = get_object_or_404(Scenario, pk=scenario_id)
        #selected_bmps = get_selected_bmps(target_dict)
        scenario.bmps = {'source_items': source_dict, 'target_items': target_dict}#, 'selected_bmps': selected_bmps}
        scenario.save()
    except Exception as e:
        print(e)
        return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'success'})

def filter_bmps(input_dict, target_list):
    selected_bmps = {}
    non_selected_bmps = {}

    for key, value in input_dict.items():
        selected_values = []
        non_selected_values = []
        for num in value:
            if num in target_list:
                selected_values.append(num)
            else:
                non_selected_values.append(num)
        
        if selected_values:
            selected_bmps[key] = selected_values
        if non_selected_values:
            non_selected_bmps[key] = non_selected_values

    return selected_bmps, non_selected_bmps



class BmpSelectionView(LoginRequiredMixin, TemplateView):

    template_name = 'step_3/bmp_selection.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scenario_id = self.kwargs.get('id')  # Assuming you're passing the ID in the URL
        scenario = Scenario.objects.get(pk=scenario_id)
        counties = scenario.base_scenario.geographic_areas.all()
        counties_list = ", ".join([county.name for county in counties])


        #context['scenario_info'] = ScenarioInfo.objects.get(pk=scenario.scenario_info.id)
        #context['counties'] = scenario
        selected_bmps = scenario.bmps
        if selected_bmps in (None, {}):
            source_items = {
            }
            target_items_category = {
                bmp_category.name: [bmp.id for bmp in Bmp.objects.filter(bmp_category=bmp_category.id)]
                for bmp_category in BmpCategory.objects.all()
            }

            target_items_category.pop('Policy')  # Removes 'b': 2 and returns 2

            target_items_type = {
                bmp_type.name: [bmp.id for bmp in Bmp.objects.filter(bmp_type=bmp_type.id).exclude(bmp_category=4)]
                for bmp_type in BmpType.objects.all()
            }
            target_items_sector = {
                sector.name: [bmp.id for bmp in Bmp.objects.filter(sector=sector.id)]
                for sector in Sector.objects.all()
            }
            target_items_sector.pop('Wastewater')
            target_items = {**target_items_category, **target_items_type, **target_items_sector}
            # Work: BmpType=5 (Animal Manure) 35 , 203 , 204 , 206 
            # Does not Work: BmpType=5 (Animal Manure) 69, 71, 135,  205
            # BmpCategoryId=2 35 , 69 , 71 , 135 , 203 , 204 , 205 , 206
            # Manure Transport approved = 31
            # Manure Transport not working: 32, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274

            animal_to_remove = [69, 135, 205] #71
            for key, values in target_items.items():
                target_items[key] = [value for value in values if value not in animal_to_remove]
            manure_to_remove = [274]#32, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273] 
            for key, values in target_items.items():
                target_items[key] = [value for value in values if value not in manure_to_remove]


            target_list= [4, 35, 206, 67, 16, 109, 111, 110, 126, 124, 125, 127, 164, 161, 163, 165, 166, 97, 86, 96, 98, 99, 221, 219, 220, 115, 106, 107, 118, 116, 117, 122, 123, 132, 150, 152, 153, 224, 222, 223, 225, 226, 169, 167, 168, 214, 215, 218, 216, 217, 50, 48, 49, 54, 55, 51, 52, 156, 154, 155, 159, 160, 157, 158, 58, 56, 57, 80, 83, 72, 73, 253, 254, 255, 112, 239, 240, 241, 242, 130, 53, 243, 244, 245, 246, 113, 114, 95, 105, 227, 228, 231, 232, 229, 230, 247, 248, 251, 252, 249, 250, 233, 234, 237, 238, 235, 236, 136, 71, 25, 63, 64, 208, 209, 210, 100, 101, 102, 103, 104, 284, 285, 9, 66, 283, 287, 61, 282, 288, 281, 289, 41, 40, 108, 266, 267, 271, 272, 273, 268, 269, 270, 82, 85, 81, 84, 79, 31, 260, 274, 257, 265, 261, 259, 258, 262, 263, 264, 256, 24, 6, 147, 148, 139, 137, 142, 141, 138, 143, 144, 145, 146, 29, 175, 76, 176, 173, 77, 174, 203, 30, 121, 201, 3, 129, 170, 128, 11, 62, 286, 23, 5, 78, 172, 36, 37, 277, 278, 291, 279, 292, 280, 293, 275, 276, 290]
            #Landuse Change': [9, 11, 61, 62, 66, 275, 276, 277, 278, 279, 280], 
            target_items2, source_items2 = filter_bmps(target_items, target_list)
            #selected_bmps2 = get_selected_bmps(target_items2)
            #selected_bmps = get_selected_bmps(target_items)

            #missing_elements = list(set(target_list) - set(selected_bmps2))


            selected_bmps = {'source_items': source_items, 'target_items': target_items}#, 'selected_bmps': selected_bmps}
            #selected_bmps = {'source_items': source_items2, 'target_items': target_items2}#, 'selected_bmps': selected_bmps2}
            scenario.bmps = selected_bmps
            scenario.save()


        '''
        target_items = {
            bmp_category.name: [(bmp.id, bmp.name) for bmp in Bmp.objects.filter(bmp_category=bmp_category)]
            for bmp_category in BmpCategory.objects.all()
        }
        '''
        contains_manure_transport = False
        stored_target_items = selected_bmps['target_items']
        stored_source_items = selected_bmps['source_items']
        animal_to_remove = [69, 135, 205] #71
        manure_to_remove = [274]#32, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274] 
        for key, values in stored_target_items.items():
            stored_target_items[key] = [value for value in values if value not in animal_to_remove]
            if 31 in values:
                contains_manure_transport = True
        for key, values in stored_target_items.items():
            stored_target_items[key] = [value for value in values if value not in manure_to_remove]
            if 31 in values:
                contains_manure_transport = True

        for key, values in stored_source_items.items():
            stored_source_items[key] = [value for value in values if value not in animal_to_remove]
        for key, values in stored_source_items.items():
            stored_source_items[key] = [value for value in values if value not in manure_to_remove]

        bmps = { bmp.id: bmp.name for bmp in Bmp.objects.all() }
        target_items = {}
        for category, items in stored_target_items.items():
            if items:
                target_items[category] = [(item, bmps[item]) for item in items] 

        source_items = {}
        for category, items in stored_source_items.items():
            if items:
                source_items[category] = [(item, bmps[item]) for item in items] 
        


        # Extract the lists
        context['counties'] = counties_list
        context['scenario_info'] = ScenarioInfo.objects.get(pk=scenario.scenario_info.id)
        context['source_items'] = source_items
        context['target_items'] = target_items
        context['current_stage'] = 4
        context['previous_stage'] = 3
        context['next_stage'] = 5
        context['scenario_id'] = scenario_id
        context['bmps'] = bmps
        context['contains_manure_transport'] = contains_manure_transport
        return context

class BmpSelectionExecView(LoginRequiredMixin, TemplateView):

    template_name = 'step_3/bmp_selection_by_exec.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        execution_id = self.kwargs.get('id')  # Assuming you're passing the ID in the URL
        execution = Execution.objects.get(pk=execution_id)


        context['scenario_info'] = ScenarioInfo.objects.get(pk=execution.scenario.scenario_info.id)
        selected_bmps = execution.bmps
        bmps = { bmp.id: bmp.name for bmp in Bmp.objects.all() }
        target_items = {}
        for category, items in selected_bmps['target_items'].items():
            target_items[category] = [(item, bmps[item]) for item in items] 

        source_items = {}
        for category, items in selected_bmps['source_items'].items():
            source_items[category] = [(item, bmps[item]) for item in items] 
        


        # Extract the lists
        context['source_items'] = source_items
        context['target_items'] = target_items
        context['current_stage'] = 4
        context['previous_stage'] = 3
        context['next_stage'] = 5
        context['execution_id'] = execution_id
        context['bmps'] = bmps
        return context

