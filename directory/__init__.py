# -*- coding: utf-8 -*-
###############################################################

from importlib import import_module

from directory.version import VERSION
from django import forms
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from phonenumbers import PhoneNumberFormat
from phonenumbers.phonenumberutil import region_code_for_number

from . import conf

###############################################################

default_app_config = "directory.apps.DirectoryConfig"

DEFAULT_REGION = getattr(settings, "PHONENUMBER_DEFAULT_REGION", None)

###############################################################


def _format_phonenumber(value):
    number_region = region_code_for_number(value)
    if DEFAULT_REGION != number_region:
        formatter = PhoneNumberFormat.INTERNATIONAL
    else:
        formatter = PhoneNumberFormat.NATIONAL
    fv = value.format_as(formatter)
    # use the raw input if all else fails...
    # (Can happen when PHONENUMBER_DEFAULT_REGION is not set)
    if fv is None or fv == "None":
        fv = value.raw_input
    return fv


# Monkey patch phone number display... (like PhoneNumberInternationalFallbackWidget)
PhoneNumber.__str__ = _format_phonenumber

###############################################################


def get_local_field(localflavor_string):
    """
    Translate a string, like 'django_localflavor_ca.forms.CAPhoneNumberField',
    into an actual field widget.
    """
    module_name, field_name = localflavor_string.rsplit(".", 1)
    f = getattr(import_module(module_name), field_name)
    return f


###############################################################

_localflav = models.CharField  # give South something to work against.

###############################################################


def localflavor_field_factory(name, desc, max_length, setting_name):

    localflavor_settings = conf.get("localflavor")
    field_string = localflavor_settings[setting_name]
    _form_field = get_local_field(field_string) if field_string is not None else None

    class _localflav(models.CharField):

        description = desc
        field_name = name

        def __init__(self, *args, **kwargs):
            kwargs["max_length"] = max_length
            self.required = True
            if "blank" in kwargs:
                self.required = not kwargs["blank"]
            super(_localflav, self).__init__(*args, **kwargs)

        def formfield(self, **kwargs):
            if field_string is not None:
                if "required" not in kwargs:
                    kwargs["required"] = self.required
                return _form_field(**kwargs)
            return super(_localflav, self).formfield(**kwargs)

        def south_field_triple(self):
            "Returns a suitable description of this field for South."
            # We'll just introspect the _actual_ field.
            from south.modelsinspector import introspector

            field_class = self.__class__.__module__ + "." + self.field_name
            args, kwargs = introspector(self)
            # found out the hard way that field_class cannot be unicode.
            return (field_class, args, kwargs)

    return _localflav


###############################################################

RegionField = localflavor_field_factory(
    "RegionField", "Region, Province, Territory, State, …", 64, "region"
)
PostalCodeField = localflavor_field_factory(
    "PostalCodeField", "Postal code, ZIP code, …", 16, "postalcode"
)

###############################################################
