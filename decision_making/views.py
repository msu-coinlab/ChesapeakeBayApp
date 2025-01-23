from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from step_4.forms import BmpCostSelectionForm
from core.models import BmpCostCustom, Scenario
from bokeh.embed import server_document
from django.shortcuts import render

# import bokeh_url variable  from cast.settings.py 
from cast.settings import BOKEH_URL 

class DecisionMakingView(LoginRequiredMixin, TemplateView):
    template_name = 'decision_making/multiplot.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scenario_id = self.kwargs.get('id')  # Assuming you're passing the ID in the URL
        scenario = Scenario.objects.get(pk=scenario_id)
        uuid = str(scenario.base_scenario.uuid)
        context['scenario_id'] = scenario_id
        file_path = "/home/gtoscano/projects/Interactive/InteractiveDecisionMaking/scatterplot/which.txt"  # Replace with your file's path

        
        try:
            with open(file_path, 'w') as file:
                file.write(uuid)
        except Exception as e:
            print(f"An error occurred: {e}")


        #script = server_document('http://localhost:5007/multiplotall')
        #print (BOKEH_URL)
        script = server_document('https://bokeh.toscano.mx/multiplotall')
        context['script'] = script

        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        form = BmpCostSelectionForm(request.POST)
        scenario_id = self.kwargs.get('id')
        if form.is_valid():
            bmp = form.cleaned_data['bmp']
            state = form.cleaned_data['state']
            new_cost = form.cleaned_data['new_cost']

            bmp_cost, created = BmpCost.objects.get_or_create(bmp=bmp, state=state)
            original_cost = bmp_cost.cost
            BmpCostCustom.objects.create(bmp_cost=bmp_cost, original_cost=original_cost, new_cost=new_cost, user=request.user)


            redirect_url = f'/step_4/{scenario_id}/'
            return redirect(redirect_url)  # Replace with your success URL
        else:
            return render(request, self.template_name, self.get_context_data(form=form))

