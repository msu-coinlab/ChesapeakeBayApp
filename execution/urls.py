from django.urls import path
from . import views

urlpatterns = [
        path('list/<int:id>/', views.ListExecutions.as_view(), name='list_executions'),
        path('create/', views.CreateExecution.as_view(), name='create_execution'),
        #path('update/<int:pk>/', views.UpdateExecution.as_view(), name='update_execution'),
        path('view/<int:id>/', views.ViewExecution.as_view(), name='view_execution'),

]

