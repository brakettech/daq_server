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
    label = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    experiment = models.ForeignKey('main.Experiment')
    last_modified= models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.label:
            self.label = str(self)
        super(Configuration, self).save(*args, **kwargs)

    def __str__(self):
        if self.label:
            return self.label
        else:
            return 'Config_{:04d}_{}'.format(self.id, self.last_modified)


class Description(models.Model):
    notes = models.ForeignKey('main.Configuration')
    name = models.CharField(max_length=CHAR_LENGTH)
    value = models.TextField()

    def __str__(self):
        return self.name


class Parameter(models.Model):
    notes = models.ForeignKey('main.Configuration')
    name = models.CharField(max_length=CHAR_LENGTH)
    value = models.CharField(max_length=CHAR_LENGTH)
    type = models.CharField(max_length=CHAR_LENGTH, choices=TYPE_CHOICES)

    def __str__(self):
        return self.name


class EntryInlineAdmin(admin.TabularInline):
    model = Parameter

    def has_change_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def get_extra(self, request, obj=None, **kwargs):
        return 0


class DescriptionInlineAdmin(admin.TabularInline):
    model = Description

    def has_change_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def get_extra(self, request, obj=None, **kwargs):
        return 0


@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    inlines = [
        EntryInlineAdmin,
        DescriptionInlineAdmin

    ]

class ConfigurationInlineAdmin(admin.TabularInline):
    model = Configuration

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def get_extra(self, request, obj=None, **kwargs):
        return 0

    def show_change_link(self):
        return True


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    inlines = [
        ConfigurationInlineAdmin,
    ]
