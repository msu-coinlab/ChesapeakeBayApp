from django.urls import path
from . import views

urlpatterns = [
    path('<int:id>/', views.BmpCostView.as_view(), name='step_4'),
    path('delete/<int:id>/', views.DeleteBmpCostCustom.as_view(), name='delete_bmp_cost_custom'),
    # Add a path for HTMX request handling
    path('<int:id>/update_table/', views.UpdateBmpCostTable.as_view(), name='update_bmp_cost_table'),
]
