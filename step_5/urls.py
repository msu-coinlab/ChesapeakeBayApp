from django.urls import path
from . import views

urlpatterns = [
    path('<int:id>/', views.BmpConstraintView.as_view(), name='step_5'),
]
