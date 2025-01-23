"""
URL configuration for cast project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import debug_toolbar
from .views import health_check


urlpatterns = [
    # other patterns…
    path("select2/", include("django_select2.urls")),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('core.urls')),
    path('scenario/', include('scenario.urls')),
    path('execution/', include('execution.urls')),
    path('solution/', include('solution.urls')),
    path('step_1/', include('step_1.urls')),
    path('step_2/', include('step_2.urls')),
    path('step_3/', include('step_3.urls')),
    path('step_3_5/', include('step_3_5.urls')),
    path('step_4/', include('step_4.urls')),
    path('step_5/', include('step_5.urls')),
    path('step_6/', include('step_6.urls')),
    path('email_templates/', include('emails.urls_template', namespace='email_templates')),
    path('optimization/', include('optimization.urls')),
    path('decision_making/', include('decision_making.urls')),
    path('api4opt/', include('api.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('__debug__/', include(debug_toolbar.urls)),
    path('health/', health_check, name='health_check'),
]

# ... your other url patterns

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
