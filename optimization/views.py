from django.shortcuts import render
from django.views.generic import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from core.tasks import process_new_optimization


class OptimizationView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        # Your logic here
        # You can access the scenario_id from kwargs['id']
        # Perform any required operations
        # Redirect to the desired URL
        messages.info(self.request, 'Optimizing scenario... Please wait.')
        scenario_id = self.kwargs.get('id')  # Assuming you're passing the ID in the URL
        process_new_optimization.delay(scenario_id)
        
        return reverse_lazy('list_scenarios')  # Redirect to list-scenarios URL
