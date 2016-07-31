"""
Tools for generating forms based on Walrus models
(cribbed from wtfpeewee)
(which was cribbed from wtforms.ext.django)
"""

from collections import namedtuple
from wtforms import Form
from wtforms import fields as f
from wtforms import validators

from walrus import AutoIncrementField
from walrus import BooleanField
from walrus import ByteField
from walrus import DateField
from walrus import DateTimeField
from walrus import FloatField
from walrus import HashField
from walrus import IntegerField
from walrus import JSONField
from walrus import ListField
from walrus import SetField
from walrus import TextField
from walrus import UUIDField
from walrus import ZSetField


__all__ = (
    'FieldInfo',
    'ModelConverter',
    'model_fields',
    'model_form')

def handle_null_filter(data):
    if data == '':
        return None
    return data

FieldInfo = namedtuple('FieldInfo', ('name', 'field'))

class ModelConverter(object):
    defaults = {
        AutoIncrementField: f.TextField,
        BooleanField: f.BooleanField,
        ByteField: f.TextField,
        DateField: f.TextField,
        DateTimeField: f.TextField,
        FloatField: f.FloatField,
        # HashField: f.HiddenField,
        IntegerField: f.IntegerField,
        JSONField: f.TextField,
        # ListField: f.HiddenField,
        # SetField: f.HiddenField,
        TextField: f.TextField,
        UUIDField: f.TextField,
        # ZSetField: f.HiddenField,
    }
    # TODO: add support for unsupported fields
    # and remove the list (i mean tuple) below
    unsupported_fields = (
        HashField,
        ListField,
        SetField,
        ZSetField,
    )
    coerce_defaults = {
        FloatField: float,
        IntegerField: int,
        TextField: unicode,
    }
    required = () # No required fields, as of now

    def __init__(self, additional=None, additional_coerce=None, overrides=None):
        #self.converters = {ForeignKeyField: self.handle_foreign_key}
        self.converters = {}
        if additional:
            self.converters.update(additional)

        self.coerce_settings = dict(self.coerce_defaults)
        if additional_coerce:
            self.coerce_settings.update(additional_coerce)

        self.overrides = overrides or {}

    def convert(self, model, field, field_args):
        # Hack: ignore temporarily unsupported fields
        if isinstance(field, self.unsupported_fields):
            return FieldInfo(field.name, None)

        kwargs = {
            'label': field.name,
            'validators': [],
            'filters': [],
            'default': field._default}
        if field_args:
            kwargs.update(field_args)

        if kwargs['validators']:
            # Create a copy of the list since we will be modifying it.
            kwargs['validators'] = list(kwargs['validators'])

        if hasattr(field, '_null') and field._null:
            # Treat empty string as None when converting.
            # Note: not actually implemented for walrus models
            kwargs['filters'].append(handle_null_filter)

        if (field._default is not None):
            # If the field can be empty, or has a default value, do not require
            # it when submitting a form.
            kwargs['validators'].append(validators.Optional())
        else:
            if isinstance(field, self.required) or field._primary_key:
                kwargs['validators'].append(validators.Required())

        if field.name in self.overrides:
            return FieldInfo(field.name, self.overrides[field.name](**kwargs))

        for converter in self.converters:
            if isinstance(field, converter):
                return self.converters[converter](model, field, **kwargs)
        else:
            for converter in self.defaults:
                if isinstance(field, converter):
                    if issubclass(self.defaults[converter], f.FormField):
                        # FormField fields (i.e. for nested forms) do not support
                        # filters.
                        kwargs.pop('filters')
                    if 'choices' in kwargs: # choices cannot be set by model
                        choices = kwargs.pop('choices', None)
                        if converter in self.coerce_settings or 'coerce' in kwargs:
                            coerce_fn = kwargs.pop('coerce',
                                                   self.coerce_settings[converter])
                            allow_blank = kwargs.pop('allow_blank', field.null)
                            kwargs.update({
                                'choices': choices,
                                'coerce': coerce_fn,
                                'allow_blank': allow_blank})

                            return FieldInfo(field.name, SelectChoicesField(**kwargs))

                    return FieldInfo(field.name, self.defaults[converter](**kwargs))

        raise AttributeError("There is not possible conversion "
                             "for '%s'" % type(field))


def model_fields(model, allow_pk=False, only=None, exclude=None,
                 field_args=None, converter=None):
    """
    Generate a dictionary of fields for a given Walrus model.

    See `model_form` docstring for description of parameters.
    """
    converter = converter or ModelConverter()
    field_args = field_args or {}

    model_fields = list(getattr(model, field) for field in model._fields)

    if only:
        model_fields = [x for x in model_fields if x.name in only]
    elif exclude:
        model_fields = [x for x in model_fields if x.name not in exclude]

    field_dict = {}
    for model_field in model_fields:
        name, field = converter.convert(
            model,
            model_field,
            field_args.get(model_field.name))
        field_dict[name] = field

    return field_dict


def model_form(model, base_class=Form, allow_pk=False, only=None, exclude=None,
               field_args=None, converter=None):
    """
    Create a wtforms Form for a given Walrus model class::

        from walrusmodel.orm import model_form
        from myproject.myapp.models import User
        UserForm = model_form(User)

    :param model:
        A Walrus model class
    :param base_class:
        Base form class to extend from. Must be a ``wtforms.Form`` subclass.
    :param only:
        An optional iterable with the property names that should be included in
        the form. Only these properties will have fields.
    :param exclude:
        An optional iterable with the property names that should be excluded
        from the form. All other properties will have fields.
    :param field_args:
        An optional dictionary of field names mapping to keyword arguments used
        to construct each field object.
    :param converter:
        A converter to generate the fields based on the model properties. If
        not set, ``ModelConverter`` is used.
    """
    field_dict = model_fields(model, allow_pk, only, exclude, field_args, converter)
    return type(model.__name__ + 'Form', (base_class, ), field_dict)
