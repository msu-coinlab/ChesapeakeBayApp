

from django.urls import path
from . import views

urlpatterns = [
    path('<int:id>/', views.ManureCountySelectionView.as_view(), name='step_3_5'),
    path('update-selected-items/', views.update_selected_items, name='update_selected_items'),
]
