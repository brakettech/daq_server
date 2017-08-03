from django.db import models
from django.contrib import admin

CHAR_LENGTH = 1000

TYPE_CHOICES = [
    ('str', 'String'),
    ('int', 'Integer'),
    ('float', 'Float'),
]

class Experiment(models.Model):
    experiment_name = models.CharField(max_length=CHAR_LENGTH, default='Setup')

    def __str__(self):
        return self.experiment_name


class Configuration(models.Model):
    name = models.CharField(max_length=CHAR_LENGTH)
    experiment = models.ForeignKey('main.Experiment')
    notes = models.TextField()

    def __str__(self):
        return self.name


class Parameter(models.Model):
    configuration = models.ForeignKey('main.Configuration')
    name = models.CharField(max_length=CHAR_LENGTH)
    value = models.CharField(max_length=CHAR_LENGTH)
    type = models.CharField(max_length=CHAR_LENGTH, choices=TYPE_CHOICES)

    def __str__(self):
        return self.name



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
