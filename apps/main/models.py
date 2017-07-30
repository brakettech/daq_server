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


class Description(models.Model):
    notes = models.ForeignKey('main.Experiment')
    name = models.CharField(max_length=CHAR_LENGTH)
    value = models.TextField()

    def __str__(self):
        return self.name


class Parameter(models.Model):
    notes = models.ForeignKey('main.Experiment')
    name = models.CharField(max_length=CHAR_LENGTH)
    value = models.CharField(max_length=CHAR_LENGTH)
    type = models.CharField(max_length=CHAR_LENGTH, choices=TYPE_CHOICES)

    def __str__(self):
        return self.name


class EntryInlineAdmin(admin.TabularInline):
    model = Parameter

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def get_extra(self, request, obj=None, **kwargs):
        return 0


class DescriptionInlineAdmin(admin.TabularInline):
    model = Description

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def get_extra(self, request, obj=None, **kwargs):
        return 0

@admin.register(Experiment)
class NoteAdmin(admin.ModelAdmin):
    inlines = [
        EntryInlineAdmin,
        DescriptionInlineAdmin

    ]

# class NoteKind(models.Model):
#     name = models.CharField(max_length=CHAR_LENGTH)
#     type = models.CharField(max_length=CHAR_LENGTH, choices=TYPE_CHOICES)

    # def __str__(self):
    #     return self.name
    #


# @admin.register(NoteKind)
# class NoteKindAdmin(admin.ModelAdmin):
#     pass

# class NoteKindInlineAdmin(admin.TabularInline):
#     model = NoteKind

# class Note(models.Model):
#     note_config = models.ForeignKey('main.NoteKind')
#     file = models.ForeignKey('main.File')
#     value = models.CharField(max_length=CHAR_LENGTH)


# @admin.register(Note)
# class NoteAdmin(admin.ModelAdmin):
#     pass

# class NoteInlineAdmin(admin.TabularInline):
#     model = Note

# # Model for handling files
# class File(models.Model):
#     csv_name = models.CharField(max_length=CHAR_LENGTH)
#     nc_name = models.CharField(max_length=CHAR_LENGTH)


# @admin.register(File)
# class FileAdmin(admin.ModelAdmin):
#     inlines = [
#         NoteInlineAdmin,
#     ]


# # # Model for handling files
# # class File(models.Model):
# #     csv_name = models.CharField(max_length=CHAR_LENGTH)
# #     nc_name = models.CharField(max_length=CHAR_LENGTH)
# #
# #
# # @admin.register(File)
# # class FileAdmin(admin.ModelAdmin):
# #     pass
# #
# #
# # class Notes(models.Model):
# #     schema = models.ForeignKey('main.Schema')
# #
# #
# # @admin.register(Notes)
# # class NoteAdmin(admin.ModelAdmin):
# #     pass
# #
# #
# # class Schema(models.Model):
# #     name = models.CharField(max_length=CHAR_LENGTH)
# #
# #
# # @admin.register(Schema)
# # class SchemaAdmin(admin.ModelAdmin):
# #     pass
# #
# #
# # # Model for handling meta data
# # class Field(models.Model):
# #     schema = models.ForeignKey('main.Schema')
# #     param_name = models.CharField(max_length=CHAR_LENGTH)
# #     param_type = models.CharField(max_length=CHAR_LENGTH)
# #
# #
# # @admin.register(Field)
# # class FieldAdmin(admin.ModelAdmin):
# #     pass
# #
# #
# # class ParamRecord(models.Model):
# #     notes = models.ForeignKey('main.Notes')
# #     field = models.ForeignKey('main.Field')
# #     value = models.BinaryField()
# #
# #
# # @admin.register(ParamRecord)
# # class ParamRecordAdmin(admin.ModelAdmin):
# #     pass
# #

