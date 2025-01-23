
from django.urls import path
from . import views

urlpatterns = [
    path('<int:id>/', views.DecisionMakingView.as_view(), name='decision_making'),
]
