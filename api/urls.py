from django.urls import path
from django.urls.conf import include
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()

#router.register('hello', views.say_hello, basename='hello')
#router.register('bases', views.BaseViewSet, basename='base')
#router.register('evaluations', views.EvaluationViewSet, basename='evaluations')
#router.register('executions', views.ExecutionViewSet, basename='executions')
#router.register('plots', views.PlotViewSet, basename='plots')
#base_router = routers.NestedDefaultRouter(
#    router, 'bases', lookup='base')
#base_router.register(
#    'files', views.BaseFileViewSet, basename='base-files')
#
#
#urlpatterns = router.urls#  + base_router.urls

urlpatterns = [ path('hello/', views.say_hello), ]
