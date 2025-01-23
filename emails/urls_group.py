
from django.urls import path, include

from . import views 

app_name = 'emailing-groups'
urlpatterns = [
    path('create-groups/', views.CreateEmailGroups.as_view(), name='create-groups'),
    path('list-email-groups/', views.ListEmailGroups.as_view(), name='list_email_groups'),
    path('create-email-group/', views.CreateEmailGroup.as_view(), name='create_email_group'),
    path('update-email-group/<slug:slug>/', views.UpdateEmailGroup.as_view(), name='update_email_group'),
    path('delete-email-group/<slug:slug>/', views.DeleteEmailGroup.as_view(), name='delete_email_group'),
    path('email-groups/<slug:slug>/', views.EmailGroupView.as_view(), name='email_group'),
    ]
