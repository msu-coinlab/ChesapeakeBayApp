from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('your_view/', views.my_view, name='your_view_name'),
    path('your_view2/', views.BmpCostCreateView.as_view(), name='your_view_name2'),
    path('your_view3/', views.BmpCostCreateView3.as_view(), name='your_view_name3'),
    path('ajax_view/', views.load_cost_and_unit, name='load_cost_and_unit'),
    path('load_unit/', views.load_unit, name='load_unit'),
]
