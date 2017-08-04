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
from apps.main.models import Experiment

from django import forms
from django.views.generic.base import TemplateView
from django.views.generic import FormView

def form_getter(chosen_experiment=None):
    experiments = list(Experiment.objects.all().order_by('name').values_list('id', 'name'))
    print('experiments', experiments)

    class MyForm(forms.Form):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            kwargs = dict(
                choices=experiments,
                widget=forms.Select(attrs={'style': 'width: 90%'}),
            )
            if chosen_experiment is not None:
                kwargs['initial'] = chosen_experiment

            self.fields['experiment'] = forms.ChoiceField(
                **kwargs
            )
            #self.fields['experiment']

            #self.fields['experiment'] = forms.ChoiceField(
            #    choices=experiments, widget=forms.Select(attrs={'style': 'width: 90%'})
            #)

            #self.fields['my_first'] = forms.CharField(label='First Name')
            #self.fields['my_last'] = forms.CharField(label='Last Name')
            #self.fields['my_float'] = forms.FloatField(label='Floating Number')

    return MyForm

#class ExperimentView(View):
#    template_name = 'silly.html'
#
#    def get(self, request, **kwargs):
#        context = {
#            'my_name': 'rich',
#            'form': form_getter()
#        }
#        print('get kwargs', kwargs)
#        return render(request, self.template_name, context=context)
#
#    def post(self, request, **kwargs):
#        context = {'my_name': 'rich'}
#        print('post kwargs', kwargs)
#        return render(request, self.template_name, context=context)

class ExperimentView(FormView):
    template_name = 'silly.html'

    def __init__(self, *args, **kwargs):
        self.form_class = form_getter()
        self.success_url_base = '/main/experiment'

        super().__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        print('get_context_data_kwargs', kwargs)
        context = super(ExperimentView, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        print('form data', form.cleaned_data)
        if form.cleaned_data.get('experiment'):
            self.success_url= '{}/{}'.format(self.success_url_base, str(form.cleaned_data['experiment']))
        return super(ExperimentView, self).form_valid(form)

    def get(self, request, **kwargs):
        #RUN GET_CONTEXT_DATA HERE AND UPDATE CONTEXT DICT.  THIS SHOULD THEN RENDER
        self.form_class = form_getter(kwargs.get('experiment_id'))
        print('get {}'.format(kwargs))
        return super(ExperimentView, self).get(request, **kwargs)

    def post(self, request, **kwargs):
        print('post {}'.format(kwargs))
        return super(ExperimentView, self).post(request, **kwargs)

    def get_initial(self):
        initial = super(ExperimentView, self).get_initial()
        initial['my_first'] = 'rob'
        initial['my_last'] = 'dec'
        initial['my_float'] = 3.14
        return initial

#class ExperimentView(View):
#    template_name = 'silly.html'
#
#    def get(self, request, **kwargs):
#        context = {'my_name': 'rich'}
#        print('get kwargs', kwargs)
#        return render(request, self.template_name, context=context)
#
#    def post(self, request, **kwargs):
#        context = {'my_name': 'rich'}
#        print('post kwargs', kwargs)
#        return render(request, self.template_name, context=context)

#class ExperimentView(TemplateView):
#    template_name = 'silly.html'
#
#    def get_context_data(self, **kwargs):
#        context = super(ExperimentView, self).get_context_data(**kwargs)
#        context['my_name'] = 'rob decarvalho'
#        return context
#
#    def get(self, *args, **kwargs):
#        print('args', args)
#        print('kwargs', kwargs)
#        return super(ExperimentView, self).get(*args, **kwargs)
#
#    def post(self, *args, **kwargs):
#         print('args', args)
#         print('kwargs', kwargs)
#         return super(ExperimentView, self).post(*args, **kwargs)




























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
