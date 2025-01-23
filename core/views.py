from django.shortcuts import render
from bokeh.embed import server_document
import logging
from .tasks import process_new_base_scenario, process_new_optimization
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import JsonResponse
from django.views.generic import RedirectView
#from openai import OpenAI
from django.contrib.auth.decorators import login_required

from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import BmpCost, BmpCostCustom
from django.shortcuts import redirect

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect

from django.views.generic import TemplateView

from .models import Scenario
from .models import BmpCost

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import BmpCost

from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .models import BmpCostCustom

from django.shortcuts import render
from django.http import JsonResponse
from .models import BmpCost

from django.http import JsonResponse
from django.shortcuts import render
from .forms import BmpCostForm, BmpCostSelectionForm
from .models import BmpCost, BmpCostCustom, State

from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import BmpCostCustom

from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import BmpCostCustom
#client = OpenAI()


logger = logging.getLogger(__name__)

@login_required
def index(request, conversation_id=None):
    user = request.user
    context = {
    }
    return render(request, 'core/index.html', context)



class CreateBmpCost(LoginRequiredMixin, CreateView):
    model = BmpCost
    form_class = BmpCostForm
    template_name = 'core/bmp_cost/create_bmp_cost.html'

    def form_valid(self, form):
        self.object = form.save()
        if self.request.htmx:
            costs = BmpCost.objects.all()
            return render(self.request, 'core/bmp_cost/partials/cost_table.html', {'costs': costs})
        else:
            return super().form_valid(form)

    def get_success_url(self):
        return reverse('create_bmp_cost')



class BmpCostView(LoginRequiredMixin, TemplateView):
    template_name = 'core/bmp_cost/bmp_cost_view.html'
    form_class =BmpCostSelectionForm 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            bmp = form.cleaned_data['bmp']
            state = form.cleaned_data['state']
            bmp_cost = BmpCost.objects.filter(bmp=bmp, state=state).first()
            return render(request, 'core/bmp_cost/partials/bmp_cost_details.html', {'bmp_cost': bmp_cost})
        return self.render_to_response(self.get_context_data(form=form))




class BmpCostCreateView(LoginRequiredMixin, FormView):
    template_name = 'core/bmp_cost/my_template.html'
    form_class = BmpCostSelectionForm
    success_url = '/your_view2/'  # Update with your success URL

    def form_valid(self, form):
        bmp = form.cleaned_data['bmp']
        state = form.cleaned_data['state']
        new_cost = form.cleaned_data['new_cost']

        bmp_cost, created = BmpCost.objects.get_or_create(bmp=bmp, state=state)
        original_cost = bmp_cost.cost
        BmpCostCustom.objects.create(bmp_cost=bmp_cost, original_cost=original_cost, new_cost=new_cost, user=self.request.user)

        return redirect(self.get_success_url())

    def form_invalid(self, form):
        # Handle the case of invalid form
        return super().form_invalid(form)


class BmpCostCreateView3(LoginRequiredMixin, TemplateView):
    template_name = 'core/bmp_cost/my_template.html'

    def get(self, request, *args, **kwargs):
        form = BmpCostSelectionForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = BmpCostSelectionForm(request.POST)
        if form.is_valid():
            bmp = form.cleaned_data['bmp']
            state = form.cleaned_data['state']
            new_cost = form.cleaned_data['new_cost']

            bmp_cost, created = BmpCost.objects.get_or_create(bmp=bmp, state=state)
            original_cost = bmp_cost.cost
            BmpCostCustom.objects.create(bmp_cost=bmp_cost, original_cost=original_cost, new_cost=new_cost, user=request.user)

            return redirect('/your_view3/')  # Replace with your success URL
        else:
            return render(request, self.template_name, {'form': form})




def my_view(request):
    if request.method == 'POST':
        form = BmpCostSelectionForm(request.POST)
        if form.is_valid():
            bmp = form.cleaned_data['bmp']
            state = form.cleaned_data['state']
            new_cost = form.cleaned_data['new_cost']

            # Assuming you want to get or create a BmpCost instance
            bmp_cost, created = BmpCost.objects.get_or_create(bmp=bmp, state=state)

            # Create a new BmpCostCustom instance
            BmpCostCustom.objects.create(bmp_cost=bmp_cost, new_cost=new_cost, user=request.user)
            
            # Redirect or indicate success
            return redirect('success_url')  # Replace with your success URL
    else:
        form = BmpCostSelectionForm()

    return render(request, 'core/bmp_cost/my_template.html', {'form': form})

def load_cost_and_unit(request):
    bmp_id = request.GET.get('bmp')
    state_id = request.GET.get('state')
    try:
        bmp_cost = BmpCost.objects.get(bmp_id=bmp_id, state_id=state_id)
        data = {
            'cost': str(bmp_cost.cost),
            'unit': bmp_cost.unit
        }
    except BmpCost.DoesNotExist:
        data = {'cost': 'N/A', 'unit': 'N/A'}
    return JsonResponse(data)




def load_unit(request):
    bmp_id = request.GET.get('bmp')
    try:
        bmp_cost = BmpCost.objects.filter(bmp_id=bmp_id).first()
        data = {
            'unit': bmp_cost.unit
        }
    except BmpCost.DoesNotExist:
        data = {'unit': 'N/A'}
    return JsonResponse(data)

