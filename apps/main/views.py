from django.shortcuts import render

# Create your views here.
#from django.views.generic import ListView
from django.views import View
from django.shortcuts import render
#from apps.main.models import Experiment, Configuration, Parameter, Description
from apps.main.models import Experiment
from rest_framework import viewsets
from apps.main.models import Parameter
from apps.main.serializers import ParameterSerializer


class ExperimentList(View):
    # model = Experiment
    template_name = 'silly.html'

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            {'experiments': Experiment.objects.all()})


class ParameterViewSet(viewsets.ModelViewSet):
    serializer_class = ParameterSerializer
    queryset =  Parameter.objects.all().order_by('name')
