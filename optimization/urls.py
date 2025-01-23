
from django.urls import path
from . import views

urlpatterns = [
    path('<int:id>/', views.OptimizationView.as_view(), name='optimization'),
]
