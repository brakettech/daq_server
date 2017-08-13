from pprint import pprint

from django.shortcuts import render
from django.db.models.functions import Lower

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

# def form_getter(chosen_experiment=None):
#     experiments = list(Experiment.objects.all().order_by(Lower('name')).values_list('id', 'name'))
#     class MyForm(forms.Form):
#         def __init__(self, *args, **kwargs):
#             super().__init__(*args, **kwargs)
#
#             kwargs = dict(
#                 choices=experiments,
#                 widget=forms.Select(attrs={'style': 'width: 90%'}),
#             )
#             if chosen_experiment is not None:
#                 kwargs['initial'] = chosen_experiment
#
#             self.fields['experiment'] = forms.ChoiceField(
#                 **kwargs
#             )
#
#         def clean(self):
#             print('form data: ', self.data)
#             return super().clean()
#
#     return MyForm

class MyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_class_lookup = {
            'str': forms.CharField,
            'int': forms.IntegerField,
            'float': forms.FloatField
        }

        experiments = [(e.id, e.name) for e in Experiment.objects.all().order_by(Lower('name'))]
        configs = [(c.id, c.name) for c in Configuration.objects.all().order_by(Lower('name'))]
        for param in Parameter.objects.all():
            field_class = field_class_lookup[param.type]
            self.fields['param_{}'.format(param.id)] = field_class(label=param.name)

            print(param.name, param.type)
            # self.fields['param_{}'.format(param.id)]
        self.fields['experiment'] = forms.ChoiceField(choices=experiments, widget=forms.Select())
        self.fields['configs'] = forms.ChoiceField(choices=configs, widget=forms.RadioSelect())

    def clean(self):
        print('form data: ', self.data)
        return super().clean()

class ExperimentView(FormView):
    template_name = 'main.html'
    form_class = MyForm
#
#     def __init__(self, *args, **kwargs):
#         #self.form_class = form_getter()
#         self.success_url_base = '/main/experiment'
#         self.post_data = {}
#
#         super().__init__(*args, **kwargs)
#         #self.object = Item()
#
#     #def get_form(self, form_class=None):
#
#     def get_experiment(self, experiment_id):
#         return Experiment.objects.get(id=experiment_id)
#
#     def get_configurations(self, experiment_id):
#         return list(Configuration.objects.filter(experiment_id=experiment_id).order_by(Lower('name')))
#
#     def get_params(selfself, experiment_id, config_id):
#         if config_id is None:
#             qs = Configuration.objects.filter(experiment_id=experiment_id).order_by(Lower('name'))
#             if qs.exists():
#                 config_id = qs.first().id
#             else:
#                 return []
#
#         qs = Parameter.objects.filter(configuration_id=config_id).order_by(Lower('name'))
#         # print('v'*80)
#         # for p in Parameter.objects.all():
#         #     print(p.configuration_id, p.name)
#         # print('v'*80)
#         return list(qs)
#
#
#     def get_context_data(self, **kwargs):
#         experiment_id = kwargs.get('experiment_id', Experiment.objects.first().id)
#         config_id = kwargs.get('configuration_id')
#         form_class = form_getter(experiment_id, self.post_data)
#         form = self.get_form(form_class)
#         context = super(ExperimentView, self).get_context_data(**kwargs)
#         context['experiment'] = self.get_experiment(experiment_id)
#         context['form'] = form
#         context['configurations'] = self.get_configurations(experiment_id)
#         context['params'] = self.get_params(experiment_id, config_id)
#
#         """
#         I WANT TO TRY AND CHANGE THIS TO HAVE A CURRENT_CONFIG IN THE CONTEXT
#         THAT IS POSSIBLY NONE.  I THINK I CAN CLEAN UP THE LOGIC BELOW WITH THIS.
#         I ALSO THINK IT WILL MAKE IT BETTER FOR HIGHLIGHTING CURRENTLY SELECTED CONFIG
#         AND PUSHING THE PROPER CONFIG ID INTO THE FORM
#         """
#         context['current_config_name'] = 'No Configuration Selected'
#         if context['configurations']:
#             if config_id is None:
#                 current_config = context['configurations'][0]
#                 context['current_config_name'] = current_config.name
#                 context['notes'] = current_config.notes
#             else:
#                 for config in context['configurations']:
#                     if config_id and int(config_id) == config.id:
#                         context['current_config_name'] = config.name
#                         context['notes'] = config.notes
#                         break
#
#         # from pprint import pprint
#         #
#         # print('*'*80)
#         # pprint('kwargs')
#         # print(kwargs)
#         # print('*'*80)
#         # print('context')
#         # #print('notes: '.format(repr(context['experiment'].notes)))
#         # pprint(context)
#         # print('*'*80)
#
#         '''
#         Okay.  Here's what's going on.  I just got the url to change
#         in response to choosing experiment.  I also got the configurations
#         linked to provide the proper params.
#         '''
#
#
#         return context
#
#     def form_valid(self, form):
#         print('form data', form.cleaned_data)
#         if form.cleaned_data.get('experiment'):
#             self.success_url= '{}/{}'.format(self.success_url_base, str(form.cleaned_data['experiment']))
#         return super(ExperimentView, self).form_valid(form)
#
#     def get(self, request, **kwargs):
#         context = self.get_context_data(**kwargs)
#         return self.render_to_response(context)
#
#     def post(self, request, **kwargs):
#         self.post_data = request.POST
#         print('kwargs {}'.format(kwargs))
#         print()
#         #pprint(request._post)
#         print()
#         pprint(request.POST)
#         return super(ExperimentView, self).post(request, **kwargs)
#
#     def get_initial(self):
#         initial = super(ExperimentView, self).get_initial()
#         initial['my_first'] = 'rob'
#         initial['my_last'] = 'dec'
#         initial['my_float'] = 3.14
#         return initial


############# This version worked okay with silly.html
# class ExperimentView(FormView):
#     template_name = 'main.html'
#
#     def __init__(self, *args, **kwargs):
#         #self.form_class = form_getter()
#         self.success_url_base = '/main/experiment'
#         self.post_data = {}
#
#         super().__init__(*args, **kwargs)
#         #self.object = Item()
#
#     #def get_form(self, form_class=None):
#
#     def get_experiment(self, experiment_id):
#         return Experiment.objects.get(id=experiment_id)
#
#     def get_configurations(self, experiment_id):
#         return list(Configuration.objects.filter(experiment_id=experiment_id).order_by(Lower('name')))
#
#     def get_params(selfself, experiment_id, config_id):
#         if config_id is None:
#             qs = Configuration.objects.filter(experiment_id=experiment_id).order_by(Lower('name'))
#             if qs.exists():
#                 config_id = qs.first().id
#             else:
#                 return []
#
#         qs = Parameter.objects.filter(configuration_id=config_id).order_by(Lower('name'))
#         # print('v'*80)
#         # for p in Parameter.objects.all():
#         #     print(p.configuration_id, p.name)
#         # print('v'*80)
#         return list(qs)
#
#
#     def get_context_data(self, **kwargs):
#         experiment_id = kwargs.get('experiment_id', Experiment.objects.first().id)
#         config_id = kwargs.get('configuration_id')
#         form_class = form_getter(experiment_id, self.post_data)
#         form = self.get_form(form_class)
#         context = super(ExperimentView, self).get_context_data(**kwargs)
#         context['experiment'] = self.get_experiment(experiment_id)
#         context['form'] = form
#         context['configurations'] = self.get_configurations(experiment_id)
#         context['params'] = self.get_params(experiment_id, config_id)
#
#         """
#         I WANT TO TRY AND CHANGE THIS TO HAVE A CURRENT_CONFIG IN THE CONTEXT
#         THAT IS POSSIBLY NONE.  I THINK I CAN CLEAN UP THE LOGIC BELOW WITH THIS.
#         I ALSO THINK IT WILL MAKE IT BETTER FOR HIGHLIGHTING CURRENTLY SELECTED CONFIG
#         AND PUSHING THE PROPER CONFIG ID INTO THE FORM
#         """
#         context['current_config_name'] = 'No Configuration Selected'
#         if context['configurations']:
#             if config_id is None:
#                 current_config = context['configurations'][0]
#                 context['current_config_name'] = current_config.name
#                 context['notes'] = current_config.notes
#             else:
#                 for config in context['configurations']:
#                     if config_id and int(config_id) == config.id:
#                         context['current_config_name'] = config.name
#                         context['notes'] = config.notes
#                         break
#
#         # from pprint import pprint
#         #
#         # print('*'*80)
#         # pprint('kwargs')
#         # print(kwargs)
#         # print('*'*80)
#         # print('context')
#         # #print('notes: '.format(repr(context['experiment'].notes)))
#         # pprint(context)
#         # print('*'*80)
#
#         '''
#         Okay.  Here's what's going on.  I just got the url to change
#         in response to choosing experiment.  I also got the configurations
#         linked to provide the proper params.
#         '''
#
#
#         return context
#
#     def form_valid(self, form):
#         print('form data', form.cleaned_data)
#         if form.cleaned_data.get('experiment'):
#             self.success_url= '{}/{}'.format(self.success_url_base, str(form.cleaned_data['experiment']))
#         return super(ExperimentView, self).form_valid(form)
#
#     def get(self, request, **kwargs):
#         context = self.get_context_data(**kwargs)
#         return self.render_to_response(context)
#
#     def post(self, request, **kwargs):
#         self.post_data = request.POST
#         print('kwargs {}'.format(kwargs))
#         print()
#         #pprint(request._post)
#         print()
#         pprint(request.POST)
#         return super(ExperimentView, self).post(request, **kwargs)
#
#     def get_initial(self):
#         initial = super(ExperimentView, self).get_initial()
#         initial['my_first'] = 'rob'
#         initial['my_last'] = 'dec'
#         initial['my_float'] = 3.14
#         return initial

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
