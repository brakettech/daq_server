from django.db import models, transaction
from django.contrib import admin

CHAR_LENGTH = 1000

TYPE_CHOICES = [
    ('str', 'String'),
    ('int', 'Integer'),
    ('float', 'Float'),
    ('channel', 'Channel'),
]

class Experiment(models.Model):
    name = models.CharField(max_length=CHAR_LENGTH, unique=True)

    class Meta:
        ordering = ['name']

    @transaction.atomic
    def clone(self, new_name):
        e = Experiment.objects.get(id=self.id)
        configs = Configuration.objects.filter(experiment=e)
        e.id = None
        e.name = new_name
        e.save()
        for c in configs:
            c.clone(e.id)

    def __str__(self):
        return self.name


class Configuration(models.Model):
    name = models.CharField(max_length=CHAR_LENGTH)
    experiment = models.ForeignKey('main.Experiment')
    notes = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = (('experiment', 'name'))
        ordering = ['name']

    @transaction.atomic
    def clone(self, experiment_id=None, new_name=None):
        if {experiment_id, new_name} == {None}:
            raise ValueError('Must supply either experiment_id or new_name')

        c = Configuration.objects.get(id=self.id)
        if experiment_id is None:
            experiment_id = c.experiment_id
        if new_name is not None:
            c.name = new_name
        params = Parameter.objects.filter(configuration=c)
        c.id = None
        c.experiment_id = experiment_id
        c.save()
        for p in params:
            p.clone(c.id)


    def __str__(self):
        return self.name


class ParameterQueryset(models.QuerySet):
    def as_dict(self):
        return {m.name: m.value for m in self}

class ParameterManager(models.Manager):
    def get_queryset(self):
        return ParameterQueryset(self.model)

class Parameter(models.Model):
    configuration = models.ForeignKey('main.Configuration')
    name = models.CharField(max_length=CHAR_LENGTH)
    value = models.CharField(max_length=CHAR_LENGTH, null=True)
    type = models.CharField(max_length=CHAR_LENGTH, choices=TYPE_CHOICES)

    def clone(self, config_id):
        p = Parameter.objects.get(id=self.id)
        p.id = None
        p.configuration_id = config_id
        p.save()

    class Meta:
        unique_together = (('configuration', 'name'))
        ordering = ['name']

    def __str__(self):
        return self.name

    objects = ParameterManager()



class TabularInlineBase(admin.TabularInline):
    def has_change_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def get_extra(self, request, obj=None, **kwargs):
        return 0

    def show_change_link(self):
        return True

class ParameterInlineAdmin(TabularInlineBase):
    model = Parameter


class ConfigurationInlineAdmin(TabularInlineBase):
    model = Configuration


@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    inlines = [
        ParameterInlineAdmin,
    ]


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    inlines = [
        ConfigurationInlineAdmin,
    ]
