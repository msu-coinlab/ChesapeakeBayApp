
from django.urls import path, include

from . import views 

app_name = 'email_templates'
urlpatterns = [
    path('list-email-templates/', views.ListEmailTemplates.as_view(), name='list_email_templates'),
    path('create-email-template/', views.CreateEmailTemplate.as_view(), name='create_email_template'),
    path('update-email-template/<slug:slug>/', views.UpdateEmailTemplate.as_view(), name='update_email_template'),
    path('delete-email-template/<slug:slug>/', views.DeleteEmailTemplate.as_view(), name='delete_email_template'),
    path('email-templates/<slug:slug>/', views.EmailTemplateView.as_view(), name='email_template'),
    ]
