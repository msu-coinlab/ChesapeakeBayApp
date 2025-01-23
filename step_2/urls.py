
from django.urls import path
from . import views

urlpatterns = [
    path('<int:id>/', views.LoadsView.as_view(), name='step_2'),
    path('by-exec/<int:id>/', views.LoadsExecView.as_view(), name='step_2_by_exec'),
    path('update-scenario-loads/', views.update_scenario_loads, name='update_scenario_loads'),
]
