

from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import BmpCostSelectionForm
from .tables import BmpCostCustomTable, BmpCostCustomDataTable
from core.models import BmpCostCustom
from core.models import Scenario, State, Bmp, BmpCost
from django.urls import reverse

from django.views.generic.edit import DeleteView




def get_bmps_and_states(scenario_id):
        scenario = Scenario.objects.get(pk=scenario_id)
        selected_bmps = scenario.bmps['target_items']
        selected_bmps_list = []
        for key, value in selected_bmps.items():
            if value not in selected_bmps_list:
                selected_bmps_list.extend(value)

        all_states_dict =  {state.abbreviation: state.id for state in State.objects.all()}
        states_list = []
        areas = scenario.geographic_areas.all()
        for area in areas:
            states_list.append(all_states_dict[area.state.lower()])
        print(states_list)
        states = State.objects.filter(id__in=states_list)
        bmps = Bmp.objects.filter(id__in=selected_bmps_list)
        return bmps,states

class BmpCostView(LoginRequiredMixin, TemplateView):
    template_name = 'step_4/update_costs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scenario_id = self.kwargs.get('id')  # Assuming you're passing the ID in the URL
        scenario = Scenario.objects.get(pk=scenario_id)
        costs = scenario.costs

        bmps,states = get_bmps_and_states(scenario_id)
        context['form'] = BmpCostSelectionForm(bmps=bmps, states=states)
        costs_data = []
        for bmp_cost_id, bmp_cost_data in costs.items():
            costs_data.append({'name': BmpCost.objects.get(id=bmp_cost_id).bmp.name, 'original_cost': bmp_cost_data['original_cost'], 'new_cost': bmp_cost_data['new_cost']})

        context['table'] = BmpCostCustomDataTable(costs_data)

        #context['table'] = BmpCostCustomTable(BmpCostCustom.objects.filter(user=self.request.user))
        context['scenario_id'] = scenario_id
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        scenario_id = self.kwargs.get('id')  # Assuming you're passing the ID in the URL
        print(scenario_id)
        bmps,states = get_bmps_and_states(scenario_id)
        form = BmpCostSelectionForm(request.POST, bmps=bmps, states=states)
        if form.is_valid():

            bmp = form.cleaned_data['bmp']
            state = form.cleaned_data['state']
            new_cost = form.cleaned_data['new_cost']

            bmp_cost, created = BmpCost.objects.get_or_create(bmp=bmp, state=state)
            original_cost = bmp_cost.cost
            new_cost = {bmp_cost.id: {'original_cost':float(original_cost), 'new_cost':float(new_cost)}}
            scenario = Scenario.objects.get(id=scenario_id)

            costs = scenario.costs
            if costs in (None, {}):
                costs = new_cost
            else:
                costs.update(new_cost) 
            scenario.costs = costs
            scenario.save()


            return redirect('step_4', id=scenario_id)  # Replace with your success URL
        else:
            return render(request, self.template_name, self.get_context_data(form=form))

class DeleteBmpCostCustom(LoginRequiredMixin, DeleteView):
    model = BmpCostCustom
    template_name = 'step_4/bmp_cost_custom_confirm_delete.html'  # Confirmation template

    def get_object(self, queryset=None):
        # Get the object using 'id' instead of 'pk'

        id = self.kwargs.get('id')  # Assuming you're passing the ID in the URL
        return BmpCostCustom.objects.get(id=id)
    def get_queryset(self):
        # Ensure that only the owner can delete
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)


