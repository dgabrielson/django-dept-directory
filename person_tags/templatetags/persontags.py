#######################
from __future__ import print_function, unicode_literals

from django import template

from ..models import PersonTag, PersonTaggedEntry, TagGroup

#######################

#####################################################################

register = template.Library()

#####################################################################


@register.simple_tag(takes_context=True)
def load_taggroups(context, varname):
    """
    Load the active TagGroup objects into varname of context.
    """
    context[varname] = TagGroup.objects.active()
    return ""


#####################################################################


@register.simple_tag(takes_context=True)
def load_persontags(context, varname):
    """
    Load the active TagGroup objects into varname of context.
    """
    context[varname] = PersonTag.objects.active()
    return ""


#####################################################################
