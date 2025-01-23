
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import BmpCostSelectionForm
from .tables import BmpCostCustomTable, BmpCostCustomDataTable
from core.models import BmpCostCustom
from core.models import Scenario, State, Bmp, BmpCost
from django.urls import reverse

from django.views.generic.edit import DeleteView
from django.views import View
from django.shortcuts import get_object_or_404

from core.tasks import get_selected_bmps 




class BmpCostView(LoginRequiredMixin, TemplateView):
    template_name = 'step_4/update_costs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scenario_id = self.kwargs.get('id')  # Assuming you're passing the ID in the URL
        scenario = Scenario.objects.get(pk=scenario_id)
        costs = scenario.costs
        costs_data = []
        for bmp_cost_id, bmp_cost_data in costs.items():
            bmp_cost = BmpCost.objects.get(id=bmp_cost_id)
            costs_data.append({'state':  bmp_cost.state.name, 'name': bmp_cost.bmp.name, 'original_cost': bmp_cost_data['original_cost'], 'new_cost': bmp_cost_data['new_cost']})
        states_list = scenario.loads['states']
        states = State.objects.filter(id__in=states_list)
        selected_bmps_list = get_selected_bmps(scenario.bmps['target_items'])
        bmps = Bmp.objects.filter(id__in=selected_bmps_list)
        context['form'] = BmpCostSelectionForm(bmps=bmps, states=states)

        #context['table'] = BmpCostCustomTable(BmpCostCustom.objects.filter(user=self.request.user))
        context['table'] = BmpCostCustomDataTable(costs_data)
        context['scenario_id'] = scenario_id
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())


    def post(self, request, *args, **kwargs):
        scenario_id = self.kwargs.get('id')
        scenario = get_object_or_404(Scenario, pk=scenario_id)
        states_list = scenario.loads['states']
        states = State.objects.filter(id__in=states_list)
        selected_bmps_list = get_selected_bmps(scenario.bmps['target_items'])
        bmps = Bmp.objects.filter(id__in=selected_bmps_list)
        form = BmpCostSelectionForm(request.POST, bmps=bmps, states=states)

        if form.is_valid():
            bmp = form.cleaned_data['bmp']
            state = form.cleaned_data['state']
            new_cost_value = form.cleaned_data['new_cost']

            bmp_cost, created = BmpCost.objects.get_or_create(bmp=bmp, state=state)
            original_cost = bmp_cost.cost
            new_cost = {str(bmp_cost.id): {'original_cost': float(original_cost), 'new_cost': float(new_cost_value)}}
            scenario = Scenario.objects.get(id=scenario_id)

            costs = scenario.costs
            if costs in (None, {}):
                costs = new_cost
            else:
                costs.update(new_cost)
            scenario.costs = costs
            scenario.save()

            # Check if it's an HTMX request
            if 'Hx-Request' in request.headers:
                # Prepare updated table data
                costs_data = []
                for bmp_cost_id, bmp_cost_data in costs.items():
                    bmp_cost = BmpCost.objects.get(id=bmp_cost_id)
                    costs_data.append({'state':  bmp_cost.state.name, 'name': bmp_cost.bmp.name, 'original_cost': bmp_cost_data['original_cost'], 'new_cost': bmp_cost_data['new_cost']})

                table = BmpCostCustomDataTable(costs_data)
                return render(request, 'step_4/partials/_table.html', {'table': table})

            return redirect(reverse('step_4', kwargs={'id': scenario_id}))

        else:
            if 'Hx-Request' in request.headers:
                # Return only the form as a response
                return render(request, 'step_4/partials/_form.html', {'form': form})

            return render(request, self.template_name, self.get_context_data(form=form))

    def post_working (self, request, *args, **kwargs):
        scenario_id = self.kwargs.get('id')  # Assuming you're passing the ID in the URL
        scenario = get_object_or_404(Scenario, pk=scenario_id)
        states_list = scenario.loads['states']
        states = State.objects.filter(id__in=states_list)
        selected_bmps_list = get_selected_bmps(scenario.bmps['target_items'])
        bmps = Bmp.objects.filter(id__in=selected_bmps_list)
        form = BmpCostSelectionForm(request.POST, bmps=bmps, states=states)
        if form.is_valid():

            bmp = form.cleaned_data['bmp']
            state = form.cleaned_data['state']
            new_cost = form.cleaned_data['new_cost']

            bmp_cost, created = BmpCost.objects.get_or_create(bmp=bmp, state=state)
            original_cost = bmp_cost.cost
            #BmpCostCustom.objects.create(bmp_cost=bmp_cost, original_cost=original_cost, new_cost=new_cost, user=request.user)
            ##current_bmp_cost = BmpCost.objects.get(id=bmp_cost.id)


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



class UpdateBmpCostTable(View):
    def post(self, request, *args, **kwargs):
        scenario_id = kwargs.get('id')
        scenario = get_object_or_404(Scenario, pk=scenario_id)
        states_list = scenario.loads['states']
        states = State.objects.filter(id__in=states_list)
        selected_bmps_list = get_selected_bmps(scenario.bmps['target_items'])
        bmps = Bmp.objects.filter(id__in=selected_bmps_list)
        form = BmpCostSelectionForm(request.POST, bmps=bmps, states=states)

        if form.is_valid():
            # Process form data
            bmp = form.cleaned_data['bmp']
            state = form.cleaned_data['state']
            new_cost_value = form.cleaned_data['new_cost']

            # Update or create the BmpCost object
            bmp_cost, created = BmpCost.objects.get_or_create(bmp=bmp, state=state)
            original_cost = bmp_cost.cost
            new_cost = {'original_cost': float(original_cost), 'new_cost': float(new_cost_value)}

            # Update the costs in the scenario
            costs = scenario.costs
            if costs in (None, {}):
                costs = {str(bmp_cost.id): new_cost}
            else:
                costs[str(bmp_cost.id)] = new_cost
            scenario.costs = costs 
            scenario.save()

            # Prepare updated table data
            costs_data = []
            for bmp_cost_id, bmp_cost_data in costs.items():
                bmp_cost = BmpCost.objects.get(id=bmp_cost_id)
                costs_data.append({'state':  bmp_cost.state.name, 'name': bmp_cost.bmp.name, 'original_cost': bmp_cost_data['original_cost'], 'new_cost': bmp_cost_data['new_cost']})


            table = BmpCostCustomDataTable(costs_data)
            new_form = BmpCostSelectionForm(bmps=bmps, states=states)
            #return render(request, 'partials/_table.html', {'table': table})
            return render(request, 'step_4/partials/_table.html', {'form': new_form, 'table': table})
        else:
            # If form is not valid, return the form with errors
            return render(request, 'step_4/partials/_form.html', {'form': form})
