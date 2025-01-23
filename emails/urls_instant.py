
from django.urls import path, include

from . import views 

app_name = 'emailing-instants'
urlpatterns = [

    path('list-email-instants/', views.ListEmailInstants.as_view(), name='list_email_instants'),
    path('create-email-instant/', views.CreateEmailInstant.as_view(), name='create_email_instant'),
    path('disabled-update-email-instant/<int:pk>/', views.UpdateEmailInstant.as_view(), name='disabled_update_email_instant'),
    path('update-email-instant/<int:pk>/', views.UpdateEmailInstant.as_view(), name='update_email_instant'),
    path('delete-email-instant/<int:pk>/', views.DeleteEmailInstant.as_view(), name='delete_email_instant'),
    path('email-instants/<int:pk>/', views.EmailInstantView.as_view(), name='email_instant'),
    path('dry-run-email-instants/<int:pk>/', views.DryRunEmailInstant.as_view(), name='dry_run_email_instant'),
]
