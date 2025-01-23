

from django.urls import path
from . import views

urlpatterns = [
    path('<int:id>/', views.BmpSelectionView.as_view(), name='step_3'),
    path('by_exec/<int:id>/', views.BmpSelectionExecView.as_view(), name='step_3_by_exec'),
    path('update-selected-bmps/', views.update_selected_bmps, name='update_selected_bmps'),
]
