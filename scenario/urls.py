
from django.urls import path
from . import views

urlpatterns = [
    path('list-info/', views.ListScenarioInfos.as_view(), name='list_info'),
    path('list/', views.ListScenarios.as_view(), name='list_scenarios'),
    path('create/', views.CreateScenario.as_view(), name='create_scenario'),
    path('update/<int:pk>/', views.UpdateScenario.as_view(), name='update_scenario'),
    path('view/<int:id>/', views.ViewScenario.as_view(), name='view_scenario'),
    path('share/<int:id>/', views.ShareScenario.as_view(), name='share_scenario'),
]

