
from django.urls import path
from . import views

urlpatterns = [
    path('<int:id>/', views.ScenarioInfoView.as_view(), name='step_1'),
    path('by-exec/<int:id>/', views.ScenarioInfoExecView.as_view(), name='step_1_by_exec'),
]
