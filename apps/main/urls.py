from django.conf.urls import url, include
from django.views.generic import TemplateView
#from apps.main.views import ExperimentList
from apps.main.views import (
    ExperimentListView,
    NewExperimentView,
    ConfigListView,
    DeleteExperimentView,
    DeleteConfigView,
    CloneExperimentView,
    CloneConfigView,
    ParamListView,
    NewConfigView,
    NewParamView, ChangeParamView)
from apps.main import views
from rest_framework import routers

# router = routers.DefaultRouter()
# router.register(r'parameters', views.ParamList.as_view())
#router.register(r'parameter', views.ParamDetail)

urlpatterns = [
    #url(r'^experiment/(?P<experiment_id>\d+)*/(?P<configuration_id>\d+)*$', ExperimentView.as_view()),
    url(r'^experiment/?$', ExperimentListView.as_view()),
    url(r'^experiment/(?P<experiment_id>\d+)/?$', ConfigListView.as_view()),
    url(r'^clone_experiment/(?P<experiment_id>\d+)/?$', CloneExperimentView.as_view()),
    url(r'^clone_config/(?P<config_id>\d+)/?$', CloneConfigView.as_view()),
    url(r'^new_experiment/?$', NewExperimentView.as_view()),
    url(r'^new_config/(?P<experiment_id>\d+)/?$', NewConfigView.as_view()),
    url(r'^new_param/(?P<config_id>\d+)/?$', NewParamView.as_view()),
    url(r'^change_param/params(?P<param_id>\d+)/?$', ChangeParamView.as_view()),
    url(r'^delete_experiment/(?P<pk>\d+)/?$', DeleteExperimentView.as_view()),
    url(r'^delete_config/(?P<pk>\d+)/?$', DeleteConfigView.as_view()),
    url(r'^config/(?P<config_id>\d+)/?$', ParamListView.as_view()),
    # url(r'^experiment/(?P<experiment_id>\d+)/(?P<configuration_id>\d+)/?$', ExperimentView.as_view()),
    # url(r'parameters/(?P<configuration_id>\d+)*$', views.ParamList.as_view()),
    # #url(r'parameters', views.ParamList.as_view()),
    # url(r'parameter/(?P<pk>\d+)$', views.ParamDetail.as_view())
]