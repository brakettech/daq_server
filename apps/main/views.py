from pprint import pprint

from django.shortcuts import render, redirect
from django.db.models.functions import Lower


# Create your views here.
from django.views.generic import ListView, DetailView
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
from django.views.generic import FormView, DeleteView, CreateView, UpdateView


class NewExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ['name']

class NewConfigForm(forms.ModelForm):
    class Meta:
        model = Configuration
        fields = ['name']

class DeleteExperimentView(DeleteView):
    model = Experiment
    success_url = '/main/experiment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['configs'] = Configuration.objects.filter(experiment=context['experiment']).order_by(Lower('name'))
        return context

class DeleteConfigView(DeleteView):
    model = Configuration
    # success_url = '/main/experiment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['params'] = Parameter.objects.filter(config=context['configuration']).order_by(Lower('name'))
        # context['params'] = Parameter.objects.filter(config=context['configuration']).order_by(Lower('name'))
        return context

class NewExperimentView(CreateView):
    model = Experiment
    fields = ['name']

    def get_success_url(self):
        return r'/main/experiment'


class CloneExperimentView(FormView):
    template_name = 'experiment_update_form.html'
    form_class = NewExperimentForm

    def form_valid(self, form):
        experiment = Experiment.objects.get(id=int(self.kwargs['experiment_id']))
        experiment.clone(form.cleaned_data['name'])
        return super().form_valid(form)

    def get_success_url(self):
        return r'/main/experiment'

class CloneConfigView(FormView):
    template_name = 'configuration_update_form.html'
    form_class = NewConfigForm

    def form_valid(self, form):
        config = Configuration.objects.get(id=int(self.kwargs['config_id']))
        config.clone(new_name=form.cleaned_data['name'])
        self.experiment_id = config.experiment_id
        return super().form_valid(form)

    def get_success_url(self):
        return r'/main/experiment/{}'.format(self.experiment_id)

# class CloneExperimentView(TemplateView):
#     template_name = 'experiment_update_form.html'
#
#     #def get_context_data(self, **kwargs):
#     def get(self, request, **kwargs):
#         experiment = Experiment.objects.get(id=int(kwargs['experiment_id']))
#         print()
#         print('cloning for {}'.format(kwargs))
#         context = self.get_context_data()
#         return self.render_to_response(context)
#         return redirect('/main/experiment')

# class CloneExperimentView(View):
#     def get(self, request, **kwargs):
#         experiment = Experiment.objects.get(id=int(kwargs['experiment_id']))
#         # I NEED TO PROVIDE A NEW NAME ARGUMENT TO THE EXPERIMENT ID
#         experiment.clone()
#         print()
#         print('cloning for {}'.format(kwargs))
#         return redirect('/main/experiment')


# class NewExperimentView(FormView):
#     template_name = 'new_experiment.html'
#     form_class = NewExperimentForm
#
#     def form_valid(self, form):
#         Experiment.objects.create(name=form.cleaned_data['name'])
#         return super().form_valid(form)
#

class ExperimentListView(ListView):
    model = Experiment

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)


class ConfigListView(ListView):
    model = Configuration

    def get_queryset(self):
        return Configuration.objects.filter(
            experiment_id=int(self.kwargs['experiment_id'])
        ).order_by(Lower('name'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['experiment'] = Experiment.objects.get(id=int(self.kwargs['experiment_id']))
        return context

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

# def form_getter(params):
#     class ParamForm(forms.Form):
#         type_map = {
#             'str': forms.CharField,
#             'int': forms.IntegerField,
#             'float': forms.FloatField,
#         }
#
#         def __init__(self):
#             super().__init__()
#             return
#             for param in params:
#                 field_class = self.type_map[param.type]
#                 self.fields['params{}'.format(param.id)] = field_class(initial=param.value, label=param.name)
#
#     return ParamForm

class ParamForm(forms.Form):
    type_map = {
        'str': forms.CharField,
        'int': forms.IntegerField,
        'float': forms.FloatField,
    }

class ParamListView(FormView):
    template_name = 'parameter_list.html'
    form_class = ParamForm
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._success_url = ''

    def get_success_url(self):
        return self._success_url

    def get_form(self):
        form = super().get_form()
        self._success_url = '/main/config/{}'.format(self.kwargs['config_id'])
        params = Parameter.objects.filter(configuration_id=int(self.kwargs['config_id'])).order_by(Lower('name'))
        for param in params:
            field_class = form.type_map[param.type]
            form.fields['params{}'.format(param.id)] = field_class(initial=param.value, label=param.name)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['config'] = Configuration.objects.get(id=int(self.kwargs['config_id']))
        return context

    def form_valid(self, form):
        for key, value in form.cleaned_data.items():
            param_id = int(key.replace('params', ''))
            param = Parameter.objects.get(id=param_id)
            param.value = value
            param.save()
        return super().form_valid(form)

    def post(self, request, **kwargs):
        return super().post(request, **kwargs)
    #     return self.get(*args, **kwargs)

    """
    NOW I NEED TO GET NEW CONFIGURATION AND CONFIGURATION CLONING GOING
    THEN I NEED TO ADD NEW PARAMETER CODE
    FINALLY I NEED TO WRITE TAGGING CODE
    I THINK I'LL KEEP A LIST OF TAGGED FILES IN THE DATABASE
    """



# class ParamListView(ListView):
#     model = Parameter
#
#     def get_queryset(self):
#         return Parameter.objects.filter(
#             configuration_id=int(self.kwargs['config_id'])
#         ).order_by(Lower('name'))
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['config'] = Configuration.objects.get(id=int(self.kwargs['config_id']))
#         return context
#
#     def post(self, *args, **kwargs):
#         return self.get(*args, **kwargs)



# class ExperimentEditView(FormView):
#     template_name = 'experiment_edit.html'
#     form_class = NewExperimentForm
#
#     def form_valid(self, form):
#         print('*'*80)
#         print(form.cleaned_data)
#         print('*'*80)
#         Experiment.objects.create(name=form.cleaned_data['name'])
#         return super().form_valid(form)
#
#     def get_success_url(self):
#         return r'/main/experiment'



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

# class MyForm(forms.Form):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         field_class_lookup = {
#             'str': forms.CharField,
#             'int': forms.IntegerField,
#             'float': forms.FloatField
#         }
#
#         experiments = [(e.id, e.name) for e in Experiment.objects.all().order_by(Lower('name'))]
#         configs = [(c.id, c.name) for c in Configuration.objects.all().order_by(Lower('name'))]
#         for param in Parameter.objects.all():
#             field_class = field_class_lookup[param.type]
#             self.fields['param_{}'.format(param.id)] = field_class(label=param.name)
#
#             print(param.name, param.type)
#             # self.fields['param_{}'.format(param.id)]
#         self.fields['experiment'] = forms.ChoiceField(choices=experiments, widget=forms.Select())
#         self.fields['configs'] = forms.ChoiceField(choices=configs, widget=forms.RadioSelect())
#
#     def clean(self):
#         print('form data: ', self.data)
#         return super().clean()

# class ExperimentView(FormView):
#     template_name = 'main.html'
#     form_class = MyForm
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




























# class ParamList(generics.ListCreateAPIView):
#     queryset = Parameter.objects.all()
#     serializer_class = ParameterSerializer
#
#     def get_queryset(self):
#         print('\n\nkwargs = ', self.kwargs)
#         configuration_id = self.kwargs.get('configuration_id')
#         qs = Parameter.objects.all()
#         if configuration_id:
#             qs = qs.filter(configuration_id=configuration_id)
#         return qs
#
#
#     def get(self, *args, **kwargs):
#         queryset = self.get_queryset()
#         print('args', repr(args))
#         print('kwargs', repr(kwargs))
#         return super(ParamList, self).get(*args, **kwargs)
#
#
# class ParamDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Parameter.objects.all()
#     serializer_class = ParameterSerializer
