from django.conf.urls import url, include
from django.views.generic import TemplateView
from apps.main.views import ExperimentList
from apps.main import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'parameters', views.ParameterViewSet)

urlpatterns = [
    url(r'^rob/?$', TemplateView.as_view(template_name="silly.html")),
    url(r'^rich/?$', ExperimentList.as_view()),
    url(r'^', include(router.urls))
]