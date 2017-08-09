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
from apps.main.models import Experiment, Configuration

from django import forms
from django.views.generic.base import TemplateView
from django.views.generic import FormView

def form_getter(chosen_experiment=None):
    experiments = list(Experiment.objects.all().order_by('name').values_list('id', 'name'))
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

    return MyForm




class ExperimentView(FormView):
    template_name = 'silly.html'

    def __init__(self, *args, **kwargs):
        self.form_class = form_getter()
        self.success_url_base = '/main/experiment'

        super().__init__(*args, **kwargs)
        #self.object = Item()

    def get_configurations(self, experiment_id):
        qs = Configuration.objects.filter(experiment_id=experiment_id).order_by('name')
        return qs

    def get_experiment(self, experiment_id):
        return Experiment.objects.get(id=experiment_id)

    def get_configurations(self, experiment_id):
        return Configuration.objects.filter(experiment_id=experiment_id).order_by('name')

    def get_context_data(self, **kwargs):
        experiment_id = kwargs.get('experiment_id', Experiment.objects.first().id)
        form_class = form_getter(experiment_id)
        form = self.get_form(form_class)
        context = super(ExperimentView, self).get_context_data(**kwargs)
        context['experiment'] = self.get_experiment(experiment_id)
        context['form'] = form
        context['configurations'] = self.get_configurations(experiment_id)

        '''
        Okay.  Here's what's going on.  I just got the url to change
        in response to choosing experiment.  I also got the configurations
        linked to provide the proper params.
        '''


        return context

    def form_valid(self, form):
        print('form data', form.cleaned_data)
        if form.cleaned_data.get('experiment'):
            self.success_url= '{}/{}'.format(self.success_url_base, str(form.cleaned_data['experiment']))
        return super(ExperimentView, self).form_valid(form)

    def get(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

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
