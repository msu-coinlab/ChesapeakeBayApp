from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import ScenarioInfo, Scenario, BaseScenario, Execution
from core.models import BmpCategory, Bmp, BmpType, Sector, GeographicArea
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json


def get_selected_items(selected_items):
        selected_items_list = []
        for _, value in selected_items.items():
            if value not in selected_items_list:
                selected_items_list.extend(value)
        return selected_items_list

def get_items_in_dict(data):
    items_dict = {}
    for category in data:
        category_dict = json.loads(category)
        category_label = category_dict['label']
        items = [int(item) for item in category_dict['items']]
        items_dict[category_label] = items
    return items_dict


@require_POST
def update_selected_items(request):
    data = request.POST
    try:
        source_items = data.getlist('sourceItems')
        target_items = data.getlist('targetItems')
        scenario_id = data.get('scenario_id')
        scenario_id = int(scenario_id)
        source_dict = {} if source_items is None else get_items_in_dict(source_items)
        target_dict = {} if target_items is None else get_items_in_dict(target_items)
        scenario = get_object_or_404(Scenario, pk=scenario_id)
        selected_items = get_selected_items(target_dict)
        scenario.manure_counties= {'source_items': source_dict, 'target_items': target_dict, 'selected_items': selected_items}
        scenario.save()
    except Exception as e:
        print(e)
        return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'success'})

class ManureCountySelectionView(LoginRequiredMixin, TemplateView):

    template_name = 'step_3_5/manure_county_selection.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scenario_id = self.kwargs.get('id')  # Assuming you're passing the ID in the URL
        scenario = Scenario.objects.get(pk=scenario_id)

        counties = scenario.base_scenario.geographic_areas.all()
        counties_list = ", ".join([county.name for county in counties])
        selected_items = scenario.manure_counties
        print(selected_items)

        if selected_items in (None, {}):
            source_items = {
            }
            target_items = {}
            for county in counties:
                target_items.setdefault(county.state.upper(), []). append(county.id)

            current_selected_items = get_selected_items(target_items)
            selected_items = {'source_items': source_items, 'target_items': target_items, 'selected_items': current_selected_items}

            scenario.manure_counties = selected_items
            scenario.save()

        item_names = { county.id: county.name for county in counties }
        target_items = {}
        for category, items in selected_items['target_items'].items():
            target_items[category] = [(item, item_names[item]) for item in items] 

        source_items = {}
        for category, items in selected_items['source_items'].items():
            source_items[category] = [(item, item_names[item]) for item in items] 


        # Extract the lists
        context['counties'] = counties_list
        context['scenario_info'] = ScenarioInfo.objects.get(pk=scenario.scenario_info.id)
        context['source_items'] = source_items
        context['target_items'] = target_items
        context['source_items2'] = source_items
        context['target_items2'] = target_items
        context['current_stage'] = 4
        context['previous_stage'] = 3
        context['next_stage'] = 5
        context['scenario_id'] = scenario_id
        context['item_names'] = item_names 
        return context

