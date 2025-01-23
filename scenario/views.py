from django.shortcuts import render
from django.views.generic import TemplateView
from django.urls import reverse
from django.views.generic import CreateView, UpdateView
from django.views.generic import ListView
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import ScenarioInfo, Scenario, BaseScenario, GeographicArea, State
from .tables import ScenarioInfoTable, ScenarioTable
from .filters import ScenarioInfoFilter, ScenarioFilter
from .forms import ScenarioForm
from core.tasks import process_new_base_scenario
from core.models import Bmp, BmpCategory,  BmpType
from django.http import JsonResponse

from django.views.generic import View
from django.shortcuts import redirect, get_object_or_404
from .forms import EmailForm, ScenarioShareForm
from django.contrib import messages

class ListScenarioInfos(LoginRequiredMixin, SingleTableMixin, FilterView):
    model = ScenarioInfo
    table_class = ScenarioInfoTable
    template_name = 'scenario/list_table_generic.html'
    filterset_class = ScenarioInfoFilter
    paginate_by = 40

    def get_context_data(self, **kwargs):
        ctx = super(ListScenarioInfos, self).get_context_data(**kwargs)
        ctx['page_title'] = 'Optimization Scenarios InfoWeb'
        ctx['create_title'] = 'New Optimization Scenario Info'
        return ctx

    def get_queryset(self):
        queryset = super().get_queryset()
        return self.filterset_class(self.request.GET, queryset=queryset).qs


# views.py in your Django app


def get_scenario_data(request):
    # This is a placeholder for your actual data retrieval logic
    return JsonResponse(scenario_list, safe=False)  # Return the list of scenarios as JSON

class ListScenarios(LoginRequiredMixin, SingleTableMixin, ListView):
    model = Scenario 
    table_class = ScenarioTable
    template_name = 'scenario/list_table_generic.html'
    paginate_by = 25 

    def get_queryset(self):
        """Override to filter scenarios by the logged-in user."""
        # This retrieves only the scenarios that belong to the current user.
        return Scenario.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super(ListScenarios, self).get_context_data(**kwargs)
        ctx['page_title'] = 'Optimization Scenarios'
        ctx['create_title'] = 'New Optimization Scenario'
        ctx['create_url'] = reverse('create_scenario')
        return ctx


class CreateScenario(LoginRequiredMixin, CreateView):
    model = Scenario
    form_class = ScenarioForm
    #fields = ['description', 'refund_amount']
    template_name = 'scenario/create_generic.html'

    def get_success_url(self):
        return reverse('list_scenarios')

    def form_invalid(self, form):
        # Custom behavior here
        # For example, logging the error
        print("Form is invalid! Errors:", form.errors)
        # Make sure to call the superclass's method as well to ensure the form is rendered with errors
        return super().form_invalid(form)

    def form_valid(self, form):
        geographic_areas_m2m = form.cleaned_data.get('geographic_areas')

        # Filter BaseScenarios with the same scenario_info
        base_scenarios_with_same_info = BaseScenario.objects.filter(
            scenario_info=form.instance.scenario_info
        )

        base_scenario = None
        for bs in base_scenarios_with_same_info:
            if set(bs.geographic_areas.all()) == set(geographic_areas_m2m):
                base_scenario = bs
                break
    
        if base_scenario:
            print('Using existing BaseScenario', base_scenario)
        else:
            # Create new BaseScenario instance if not exists
            base_scenario = BaseScenario.objects.create(scenario_info=form.instance.scenario_info)
            print('base_scenario', base_scenario.status)
            base_scenario.geographic_areas.set(geographic_areas_m2m)
            base_scenario.save()
            print('To Create new BaseScenario', base_scenario)
            process_new_base_scenario.delay(base_scenario.id)
            print('Created new BaseScenario', base_scenario)
        
        # Assign the BaseScenario (new or existing) to the Scenario instance
        form.instance.base_scenario = base_scenario
        form.instance.status = 'P'
        loads = {}
        loads['nitrogen'] = 30.0 
        loads['phosphorous'] = 0.0 
        loads['sediments'] = 0.0 
        loads['oxygen'] = 0.0 
        loads['optimize_by_load'] = True
        loads['lead_load'] = 'nitrogen'
        loads['total_dollars'] = 0.0
        loads['total_acres_pct'] = 100.0

        form.instance.loads = loads
        # Set the user_id before saving the Scenario instance
        form.instance.user = self.request.user
    
        # Now save the Scenario instance
        form.instance.save()
    
        # Set the many-to-many fields for the Scenario instance
        print(form.instance.geographic_areas, geographic_areas_m2m)
        form.instance.geographic_areas.set(geographic_areas_m2m)
    
        # Continue with the rest of the form handling
        return super(CreateScenario, self).form_valid(form)

    
    def get_context_data(self, **kwargs):
        ctx = super(CreateScenario, self).get_context_data(**kwargs)
        ctx['button_name'] = 'Create'
        ctx['page_title'] = 'New Optimization Scenario'
        geographic_areas = GeographicArea.objects.all() 
        states_names = {(state.abbreviation).upper() : state.name for state in State.objects.all()} 
        source_counties = {}
        for geographic_area in geographic_areas:
            if states_names[geographic_area.state] not in source_counties.keys():
                source_counties[states_names[geographic_area.state]] = [(geographic_area.id, geographic_area.name)]
            else:
                source_counties[states_names[geographic_area.state]].append((geographic_area.id, geographic_area.name))

        ctx['source_counties'] = source_counties 
        ctx['target_counties'] = {} 

        return ctx


class UpdateScenario(LoginRequiredMixin, UpdateView):
    model = Scenario 
    form_class  = ScenarioForm
    template_name = 'scenario/update_generic.html'
    context_object_name = 'object'

    def get_success_url(self):
        return reverse('list_scenarios')

    def get_context_data(self, **kwargs):
        ctx = super(UpdateScenario, self).get_context_data(**kwargs)
        ctx['next_step_url'] = 'step1'
        return ctx
# Createyour views here.

class ViewScenario(LoginRequiredMixin, TemplateView):
    template_name = 'scenario/view.html'
    model = Scenario 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scenario_id = self.kwargs.get('id')  # Assuming you're passing the ID in the URL

        scenario = Scenario.objects.get(id=scenario_id)

        counties = scenario.base_scenario.geographic_areas.all()
        counties_list = [county.name for county in counties]

        context['scenario_info'] = scenario.base_scenario.scenario_info 
        context['counties'] = counties_list 
        context['scenario_id'] = scenario_id

               
        return context



class ShareScenarios(LoginRequiredMixin, TemplateView):
    template_name = 'scenario/share_scenario.html'
    model = Scenario

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scenario_id = self.kwargs.get('id')  # Assuming you're passing the ID in the URL

        context['scenario_id'] = scenario_id
               
        return context

from core.models import User

class ShareScenario2s(LoginRequiredMixin, TemplateView):
    template_name = 'scenario/share_scenario.html'
    form_class = EmailForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'scenario_id': self.kwargs.get('id')})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            scenario_id = self.kwargs.get('id')
            scenario = get_object_or_404(Scenario, pk=scenario_id)
            
            try:
                user_to_share_with = User.objects.get(email=email)
                scenario.shared_with.add(user_to_share_with)
                messages.success(request, 'Scenario shared successfully.')
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
            
            return redirect('share_scenario', id=scenario_id)
        else:
            return render(request, self.template_name, {'form': form, 'scenario_id': self.kwargs.get('id')})


class ShareScenario(LoginRequiredMixin, View):
    template_name = 'scenario/share_scenario.html'

    def get(self, request, *args, **kwargs):
        scenario_id = self.kwargs.get('id')
        scenario = get_object_or_404(Scenario, pk=scenario_id)
        form = ScenarioShareForm(instance=scenario)
        return render(request, self.template_name, {'form': form, 'scenario_id': scenario_id})

    def post(self, request, *args, **kwargs):
        scenario_id = self.kwargs.get('id')
        scenario = get_object_or_404(Scenario, pk=scenario_id)
        form = ScenarioShareForm(request.POST, instance=scenario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Scenario sharing updated successfully.')
            return redirect('share_scenario', id=scenario_id)
        else:
            messages.error(request, 'There was an error updating the scenario sharing.')
        return render(request, self.template_name, {'form': form, 'scenario_id': scenario_id})
