"""
Reusable library of mixins.
"""
from __future__ import unicode_literals

from .admin_autocomplete import LabelAutocompleteJsonView
from .cbv_admin import ClassBasedViewsAdminMixin
from .default_filter_admin import DefaultFilterMixin
from .restricted_forms import (
    RestrictedAdminMixin,
    RestrictedFormViewMixin,
    RestrictedQuerysetMixin,
)
from .single_fk import SingleFKAdminMixin, SingleFKFormViewMixin

__all__ = [
    "LabelAutocompleteJsonView",
    "ClassBasedViewsAdminMixin",
    "DefaultFilterMixin",
    "RestrictedAdminMixin",
    "RestrictedFormViewMixin",
    "RestrictedQuerysetMixin",
    "SingleFKAdminMixin",
    "SingleFKFormViewMixin",
]
