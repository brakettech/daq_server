from pprint import pprint

from django.db import transaction
from django.db.models.functions import Lower

from django.views.generic import ListView, DetailView
from apps.main.models import Parameter, CHAR_LENGTH
from apps.main.models import Experiment, Configuration

from django import forms
from django.views.generic import FormView, DeleteView, CreateView, UpdateView

APP_NAME= 'main'

class NewExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ['name']



class NewConfigView(CreateView):
    model = Configuration
    fields = ['name', 'experiment']

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['experiment_id'] = self.kwargs['experiment_id']
        return context

    def get_form(self):
        form = super().get_form()
        form.fields['experiment'].widget = forms.HiddenInput()
        form.fields['experiment'].initial = int(self.kwargs['experiment_id'])
        return form

    def get_success_url(self):
        return r'/main/experiment/{}'.format(self.kwargs['experiment_id'])


class DeleteExperimentView(DeleteView):
    model = Experiment
    success_url = '/main/experiment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['configs'] = Configuration.objects.filter(experiment=context['experiment']).order_by(Lower('name'))
        return context

class DeleteConfigView(DeleteView):
    model = Configuration

    def get_success_url(self):
        return r'/main/experiment/{}'.format(self.get_context_data()['configuration'].experiment_id)

class DeleteParamView(DeleteView):
    model = Parameter

    def get_object(self, queryset=None):
        param = Parameter.objects.get(id=int(self.kwargs['param_id']))
        self.config_id = param.configuration_id
        return param

    def get_success_url(self):
        return r'/main/config/{}'.format(self.config_id)


class NewExperimentView(CreateView):
    model = Experiment
    fields = ['name']

    def get_success_url(self):
        return r'/main/experiment'


class CloneExperimentView(FormView):
    template_name = '{}/experiment_update_form.html'.format(APP_NAME)
    form = NewExperimentForm
    form_class = form

    def form_valid(self, form):
        experiment = Experiment.objects.get(id=int(self.kwargs['experiment_id']))
        experiment.clone(form.cleaned_data['name'])
        return super().form_valid(form)

    def get_success_url(self):
        return r'/main/experiment'


class CloneConfigForm(forms.ModelForm):
    class Meta:
        model = Configuration
        fields = ['name']

class CloneConfigView(FormView):
    template_name = '{}/configuration_update_form.html'.format(APP_NAME)
    form_class = CloneConfigForm

    def form_valid(self, form):
        config = Configuration.objects.get(id=int(self.kwargs['config_id']))
        config.clone(new_name=form.cleaned_data['name'])
        self.experiment_id = config.experiment_id
        return super().form_valid(form)

    def get_success_url(self):
        return r'/main/experiment/{}'.format(self.experiment_id)


class ExperimentListView(ListView):
    model = Experiment

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def get_queryset(self):
        return Experiment.objects.all().order_by(Lower('name'))


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


class ChangeParamView(UpdateView):
    model = Parameter
    fields = ['name', 'type']
    template_name = '{}/update_parameter_view.html'.format(APP_NAME)

    def get_object(self):
        return Parameter.objects.get(id=int(self.kwargs['param_id']))

    def get_success_url(self):
        param = self.get_object()
        url = '/main/config/{}'.format(param.configuration_id)
        print('>>>>>>>>> url {}'.format(url))
        return url

    def form_valid(self, form):
        param = self.get_object()
        if Parameter.objects.filter(configuration=param.configuration, name=form.data['name']).exists():
            form.add_error('name', 'A parameter named "{}" already exists'.format(form.data['name']))
            return self.form_invalid(form)
        return super().form_valid(form)


class NewParamView(CreateView):
    model = Parameter
    fields = ['name', 'type', 'configuration']

    def get_form(self):
        form = super().get_form()
        form.fields['configuration'].widget = forms.HiddenInput()
        form.fields['configuration'].initial = int(self.kwargs['config_id'])
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['config_id'] = self.kwargs['config_id']
        return context

    def get_success_url(self):
        return '/main/config/{}'.format(self.kwargs['config_id'])

class ParamForm(forms.Form):
    type_map = {
        'str': forms.CharField,
        'int': forms.IntegerField,
        'float': forms.FloatField,
    }


class ParamListView(FormView):
    template_name = '{}/parameter_list.html'.format(APP_NAME)
    form_class = ParamForm
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._success_url = ''

    def get_success_url(self):
        return self._success_url

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs['request'] = self.request

    def get_form(self):
        form = super().get_form()
        self._success_url = '/main/config/{}'.format(self.kwargs['config_id'])
        params = Parameter.objects.filter(configuration_id=int(self.kwargs['config_id'])).order_by(Lower('name'))
        for param in params:
            field_class = form.type_map[param.type]
            form.fields['params{}'.format(param.id)] = field_class(initial=param.value, label=param.name)

        form.fields['input_file'] = forms.FileField(label="", required=False)
        # form.fields['input_file'].required = False
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['config'] = Configuration.objects.get(id=int(self.kwargs['config_id']))
        # context['tag_form'] = TagExperimentForm()
        return context

    @transaction.atomic
    def form_valid(self, form):
        for key, value in form.cleaned_data.items():
            if 'params' in key:
                param_id = int(key.replace('params', ''))
                param = Parameter.objects.get(id=param_id)
                param.value = value
                param.save()
        if 'tag_file' in self.request.POST:

            print('xxxxxxxxxxxxxxx')
            print('*'*80)
            print(self.request.POST['tag_file'])
            print('*'*80)


        pprint(self.request.POST)
        print('-------------')
        pprint(form.cleaned_data)

        return super().form_valid(form)
