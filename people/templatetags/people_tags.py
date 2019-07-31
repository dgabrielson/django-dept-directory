"""
Template tags for the people application.
"""
from django import template
from people.models import Person

#####################################################################

register = template.Library()

#####################################################################


@register.filter
def get_person(user):
    """
    Usage: ``{{ user|get_person }}``.
    Given a user object, return the corresponding person object,
    if they exist, if not, returns None.  It's up to the template
    to deal with the truthiness of the result.
    """
    try:
        return Person.objects.get(username=user.username, active=True)
    except Person.DoesNotExist:
        return None


#####################################################################


@register.filter
def has_addl_data(person, key):
    """
    Usage: ``{% if person|has_addl_data:"initials" %}``

    Note: this will return ``False`` in the event of a key collision.
    """
    return person.personkeyvalue_set.lookup_filter(key).count() == 1


#####################################################################


@register.filter
def get_addl_data(person, key):
    """
    Usage: ``{{ person|get_addl_data:"Google Scholar ID" }}``
    """
    return person.personkeyvalue_set.lookup(key)


#####################################################################
