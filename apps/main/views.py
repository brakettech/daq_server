from django.shortcuts import render

# Create your views here.
#from django.views.generic import ListView
from django.views import View
from django.shortcuts import render
#from apps.main.models import Experiment, Configuration, Parameter, Description
from apps.main.models import Parameter
from rest_framework import viewsets, views, generics
from apps.main.models import Parameter
from apps.main.serializers import ParameterSerializer


class ParamList(generics.ListCreateAPIView):
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer

    def get_queryset(self):
        print('\n\nkwargs = ', self.kwargs)
        configuration_id = self.kwargs.get('configuration_id')
        qs = Parameter.objects.all()
        if configuration_id:
            qs = qs.filter(configuration_id=configuration_id)
        return qs


    def get(self, *args, **kwargs):
        queryset = self.get_queryset()
        print('args', repr(args))
        print('kwargs', repr(kwargs))
        return super(ParamList, self).get(*args, **kwargs)


class ParamDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer
