from django.conf.urls import url
from django.views.generic import TemplateView
from apps.main.views import ExperimentList

urlpatterns = [
    url(r'^rob/?$', TemplateView.as_view(template_name="silly.html")),
    url(r'^rich/?$', ExperimentList.as_view()),
]