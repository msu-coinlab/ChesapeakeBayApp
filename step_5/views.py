from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from step_5.forms import BmpConstraintSelectionForm
from step_5.tables import BmpConstraintCustomDataTable
from core.models import BmpCostCustom
from core.models import Scenario, State, Bmp, BmpCost
from django.urls import reverse
from django.shortcuts import get_object_or_404

class BmpConstraintView(LoginRequiredMixin, TemplateView):
    template_name = 'step_5/bmp_constraint.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scenario_id = self.kwargs.get('id')  # Assuming you're passing the ID in the URL
        scenario = Scenario.objects.get(pk=scenario_id)

        selected_bmps_list = scenario.bmps['selected_bmps']
        bmps = Bmp.objects.filter(id__in=selected_bmps_list)
        context['form'] = BmpConstraintSelectionForm(bmps=bmps)
        # Filter the table data by the current user

        bmp_constraints = scenario.bmp_constraints
        bmp_constraints_list = []
        for bmp_id, max_quantity in bmp_constraints.items():
            bmp = Bmp.objects.get(id=bmp_id)
            bmp_constraints_list.append({'name': bmp.name, 'max_quantity': max_quantity})
        context['table'] = BmpConstraintCustomDataTable(bmp_constraints_list)
        context['scenario_id'] = scenario_id
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        scenario_id = self.kwargs.get('id')
        #scenario = get_object_or_404(Scenario, pk=scenario_id)
        scenario = Scenario.objects.get(id=scenario_id)
        selected_bmps_list = scenario.bmps['selected_bmps']
        bmps = Bmp.objects.filter(id__in=selected_bmps_list)
        form = BmpConstraintSelectionForm(request.POST, bmps=bmps)

        if form.is_valid():
            bmp = form.cleaned_data['bmp']
            max_quantity = form.cleaned_data['max_quantity']
            new_max_constraint = {str(bmp.id): float(max_quantity)}
            bmp_constraints = scenario.bmp_constraints

            if bmp_constraints in (None, {}):
                bmp_constraints = new_max_constraint
            else:
                bmp_constraints.update(new_max_constraint)
            scenario.bmp_constraints = bmp_constraints
            scenario.save()

            # Check if it's an HTMX request
            if 'Hx-Request' in request.headers:
                # Prepare updated table data
                bmp_constraints_list = []
                for bmp_id, max_quantity in bmp_constraints.items():
                    bmp = Bmp.objects.get(id=bmp_id)
                    bmp_constraints_list.append({'name': bmp.name, 'max_quantity': max_quantity})

                table = BmpConstraintCustomDataTable(bmp_constraints_list)
                return render(request, 'step_5/partials/_table.html', {'table': table})

            return redirect(reverse('step_5', kwargs={'id': scenario_id}))

        else:
            if 'Hx-Request' in request.headers:
                # Return only the form as a response
                return render(request, 'step_5/partials/_form.html', {'form': form})

            return render(request, self.template_name, self.get_context_data(form=form))
       


