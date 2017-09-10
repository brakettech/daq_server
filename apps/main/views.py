import os
import pathlib
from pprint import pprint
import re

from django import forms
from django.db import transaction
from django.db.models.functions import Lower
from django.views.generic import FormView, DeleteView, CreateView, UpdateView, TemplateView
from django.views.generic import ListView
from django.utils.text import slugify

from apps.main.models import Experiment, Configuration
from apps.main.models import Parameter
from pico import Data

APP_NAME = 'main'
DEFAULT_PATH = '/daqroot'

CHANNEL_NAMES = [
    'channel_a',
    'channel_b',
    'channel_c',
    'channel_d',
]


def path_getter(uri=DEFAULT_PATH):
    if uri is None:
        uri = DEFAULT_PATH
    path = pathlib.Path(uri.replace('file:', ''))
    if not path.exists():
        path = pathlib.Path(DEFAULT_PATH)
    p = path
    parents = []
    if p.is_dir():
        parents.append(p)
    while p.as_posix() != DEFAULT_PATH:
        p = p.parent
        parents.append(p)
    parents = parents[::-1]
    if parents:
        parents = parents[1:]

    if path.is_dir():
        entries = [pth for pth in path.iterdir() if not pth.name.startswith('.')]
    else:
        entries = []
    return parents, path, entries


class NewExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ['name']


class NCView(TemplateView):
    template_name = '{}/netcdf.html'.format(APP_NAME)
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        path_uri = self.request.GET.get('path_uri')

        parents, path, entries = path_getter(path_uri)

        data = Data()
        data.load_meta(path.as_posix())

        rex_private = re.compile(r'__\S+__')
        params = {}
        for key, val in data.meta.items():
            if not rex_private.match(key) and not key == 'notes':
                params[key] = val

        context['file'] = path.as_posix()
        context['params'] = params
        context['notes'] = data.meta.get('notes', '')
        return context

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
    # form_class = ChangeParamForm
    model = Parameter
    fields = ['name', 'type']
    template_name = '{}/update_parameter_view.html'.format(APP_NAME)

    def get_object(self):
        return Parameter.objects.get(id=int(self.kwargs['param_id']))

    def get_success_url(self):
        param = self.get_object()
        url = '/main/config/{}'.format(param.configuration_id)
        return url

    def form_valid(self, form):
        param = self.get_object()
        if Parameter.objects.filter(configuration=param.configuration, name=form.data['name']).exists():
            form.add_error('name', 'A parameter named "{}" already exists'.format(form.data['name']))
            return self.form_invalid(form)
        return super().form_valid(form)


class NewParamForm(forms.ModelForm):
    class Meta:
        model = Parameter
        fields = ['name', 'type', 'configuration']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['type'] == 'channel':
            if cleaned_data['name'] not in CHANNEL_NAMES:
                self.add_error(
                    'name',
                    'Allowed channel names: {}'.format(CHANNEL_NAMES)
                )
        else:
            slug_name = slugify(cleaned_data['name']).replace('-', '_')
            if cleaned_data['name'] != slug_name:
                self.add_error('name', 'Name must be a slug like: \'{}\''.format(slug_name))

        return cleaned_data


class NewParamView(CreateView):
    form_class = NewParamForm
    model = Parameter
    # fields = ['name', 'type', 'configuration']

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


class ResultForm(forms.Form):
    def clean(self):
        cleaned_data = super().clean()
        cleaned_data.update(self.view.request.POST)
        cleaned_data.update(self.view.kwargs)
        path_uri = self.view.request.GET.get('path_uri')
        parents, path, entries = path_getter(path_uri)
        path_uri = path.parent.as_uri()
        cleaned_data.update(path_uri=path_uri)
        return cleaned_data


class TagResultView(FormView):
    template_name = '{}/tag_result.html'.format(APP_NAME)
    form_class = ResultForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._success_url = ''

    def get_form(self):
        form = super().get_form()
        form.view = self
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context.update(self.kwargs)
        return context

    def get_success_url(self):
        return self._success_url

    def form_valid(self, form):
        self._success_url = '/main/config/{}?path_uri={}'.format(
            form.cleaned_data['config_id'],
            form.cleaned_data['path_uri']
        )
        return super().form_valid(form)


class TagForm(forms.Form):
    def clean(self):
        cleaned_data = self.cleaned_data
        cleaned_data.update(dict(self.view.request.POST))
        path_uri = self.view.request.GET.get('path_uri')
        cleaned_data.update(path_uri=path_uri)
        return cleaned_data


class TagFileView(FormView):
    template_name = '{}/tag_file.html'.format(APP_NAME)
    form_class = TagForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._success_url = ''

    def get_success_url(self):
        return self._success_url

    def get_form(self):
        form = super().get_form()
        form.view = self
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        path_uri = self.request.GET.get('path_uri')
        parents, path, entries = path_getter(path_uri)

        context['csv_file'] = path
        context['netcdf_file'] = path.parent.joinpath(path.name.replace(path.suffix, '.nc'))
        context['config_id'] = self.kwargs['config_id']
        config_id = int(self.kwargs['config_id'])
        context['params'] = Parameter.objects.filter(configuration_id=config_id).order_by(Lower('name'))
        context['notes'] = Configuration.objects.get(id=config_id).notes
        return context

    def form_valid(self, form):
        # self._success_url = '/main/tag_file/{}/?path_uri={}'.format(
        if 'create' in form.cleaned_data:
            self._success_url = '/main/tag_result/{}/saved?path_uri={}'.format(
                form.cleaned_data['config_id'][0],
                form.cleaned_data['path_uri']
            )
            self.tag_file(form)
        else:
            self._success_url = '/main/tag_result/{}/canceled?path_uri={}'.format(
                form.cleaned_data['config_id'][0],
                form.cleaned_data['path_uri']
            )
        return super().form_valid(form)

    def tag_file(self, form):
        config = Configuration.objects.get(id=int(form.cleaned_data['config_id'][0]))
        params = Parameter.objects.filter(configuration=config).as_dict()
        path_uri = form.cleaned_data['path_uri']
        parents, csv_file, entries = path_getter(path_uri)
        params.update(notes=config.notes)

        nc_file = pathlib.Path(csv_file.parent.joinpath(csv_file.stem + '.nc').as_posix())
        data = Data()
        data.csv_to_netcdf(csv_file.as_posix(), nc_file.as_posix(), **params)

class ParamForm(forms.Form):
    type_map = {
        'str': forms.CharField,
        'int': forms.IntegerField,
        'float': forms.FloatField,
        'channel': forms.CharField,
    }

    def clean(self):
        clean_data = super().clean()
        error_dict = {}

        for name, value in clean_data.items():
            if name in CHANNEL_NAMES:
                value_slug = slugify(value).replace('-', '_')
                if value != value_slug:
                    error_dict[name] = 'Channel names must be slugs like: \'{}\''.format(value_slug)

        for name, error in error_dict.items():
            self.add_error(name, error)

        clean_data['selected_file'] = self.request.POST.get('selected_file')
        clean_data['current_path'] = self.request.POST.get('current_path')
        clean_data.update(self.view.kwargs)
        return clean_data


class ParamListView(FormView):
    template_name = '{}/parameter_list.html'.format(APP_NAME)
    form_class = ParamForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._success_url = ''

    def get_success_url(self):
        return self._success_url

    def get_form(self):
        form = super().get_form()
        form.request = self.request
        form.view = self

        config = Configuration.objects.get(id=int(self.kwargs['config_id']))
        form.view.populate_params(config)
        self._success_url = '/main/config/{}'.format(config.id)

        for param in self.params:
            field_class = form.type_map[param.type]
            form.fields[param.name] = field_class(
                initial=param.value, label='({}) {}'.format(param.type.lower()[0], param.name), required=False)
            # form.fields[param.name].is_param = True
        form.fields['notes'] = forms.CharField(
            initial=config.notes, required=False, widget=forms.Textarea(attrs={'style': 'height: 100%; width: 100%;'}))

        return form

    def populate_params(self, config):
        if not hasattr(self, 'params'):
            params = Parameter.objects.filter(configuration=config)
            self.params = sorted(params, key=lambda p: (p.type != 'channel', p.name))

    def populate_config(self):
        if not hasattr(self, 'config'):
            self.config = Configuration.objects.get(id=int(self.kwargs['config_id']))

    def get_context_data(self, **kwargs):
        self.populate_config()
        path_uri = self.request.GET.get('path_uri')
        parents, path, entries = path_getter(path_uri)
        netcdf_entries = [e for e in entries if e.suffix == '.nc']
        self.populate_params(self.config)

        context = super().get_context_data(**kwargs)
        context['config'] = self.config
        context['current_path'] = path
        context['entries'] = entries
        context['netcdf_files'] = netcdf_entries
        context['parents'] = parents
        context['param_names'] = [p.name for p in self.params]

        return context

    def save_params_values(self, form):
        self.populate_config()
        self.populate_params(self.config)

        # save notes
        self.config.notes = form.cleaned_data['notes']
        self.config.save()

        param_names = {p.name for p in self.params}
        # loop over all cleaned data items
        for key, value in form.cleaned_data.items():
            # if this is a parameter
            if key in param_names:
                # get the parameter object
                param = Parameter.objects.get(configuration=self.config, name=key)
                # save the new parameter value
                param.value = value
                param.save()

    def tag_file_if_needed(self, cleaned_data):
        path, file_name = cleaned_data['current_path'], cleaned_data['selected_file']
        if path and file_name:
            path = pathlib.Path(os.path.join(cleaned_data['current_path'], cleaned_data['selected_file']))
            self._success_url = '/main/tag_file/{}/?path_uri={}'.format(
                cleaned_data['config_id'],
                path.as_uri(),
            )


    @transaction.atomic
    def form_valid(self, form):
        self.save_params_values(form)
        self.tag_file_if_needed(form.cleaned_data)
        return super().form_valid(form)
