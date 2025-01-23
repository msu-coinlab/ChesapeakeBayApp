
from django.urls import path, include

from . import views 

app_name = 'emailing'
urlpatterns = [
    path('list-email-massives/', views.ListEmailMassives.as_view(), name='list_email_massives'),
    path('create-email-massive/', views.CreateEmailMassive.as_view(), name='create_email_massive'),
    path('disabled-update-email-massive/<slug:slug>/', views.UpdateEmailMassive.as_view(), name='disabled_update_email_massive'),
    path('update-email-massive/<slug:slug>/', views.UpdateEmailMassive.as_view(), name='update_email_massive'),
    path('delete-email-massive/<slug:slug>/', views.DeleteEmailMassive.as_view(), name='delete_email_massive'),
    path('email-massives/<slug:slug>/', views.EmailMassiveView.as_view(), name='email_massive'),
    path('dry-run-email-massives/<slug:slug>/', views.DryRunEmailMassive.as_view(), name='dry_run_email_massive'),
    ]
