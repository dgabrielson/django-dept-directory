"""
QuerySets for contacts.  A contact is a person and all of their associated information,
e.g., phone numbers, addresses, etc.
"""
#######################
from __future__ import print_function, unicode_literals

import operator

#######################
from functools import reduce

from django.db import models

#######################################################################


class CustomQuerySet(models.query.QuerySet):
    """
    Custom QuerySet.
    """

    def active(self):
        """
        Returns only the active items in this queryset
        """
        return self.filter(active=True)


#######################################################################


class PersonFlagQuerySet(CustomQuerySet):
    """
    QuerySet for PersonFlag objects
    """

    def slugs(self):
        """
        Return a list of slugs
        """
        return self.values_list("slug", flat=True).distinct()


#######################################################################


class PersonQuerySet(CustomQuerySet):
    """
    QuerySet for person records
    """

    def search(self, *criteria):
        """
        Magic search for people.
        This is heavily modelled after the way the Django Admin handles
        search queries.
        See: django.contrib.admin.views.main.py:ChangeList.get_query_set
        """
        if len(criteria) == 0:
            assert False, "Supply search criteria"

        search_fields = ["cn", "sn", "given_name"]
        terms = ["{}".format(c) for c in criteria]
        if len(terms) == 1:
            terms = terms[0].split()

        def construct_search(field_name):
            if field_name.startswith("^"):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith("="):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith("@"):
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name

        qs = self.filter(active=True)
        orm_lookups = [
            construct_search(str(search_field)) for search_field in search_fields
        ]
        for bit in terms:
            or_queries = [models.Q(**{orm_lookup: bit}) for orm_lookup in orm_lookups]
            qs = qs.filter(reduce(operator.or_, or_queries))

        return qs.distinct()


###############################################################


class BaseContactInfoQuerySet(CustomQuerySet):
    """
    QuerySet for ContactInfo
    """

    def public(self):
        return self.filter(active=True, public=True)

    def verified(self):
        return self.filter(active=True, verified=True)

    def preferred(self):
        return self.filter(active=True, preferred=True)


###############################################################


class PersonKeyQuerySet(CustomQuerySet):
    def lookup_filter(self, key):
        qs = self.active()
        qs = qs.filter(models.Q(slug__iexact=key) | models.Q(verbose_name__iexact=key))
        return qs.distinct()

    def lookup(self, key):
        from .models import PersonKey

        try:
            return self.lookup_filter(key).get()
        except (PersonKey.DoesNotExist, PersonKey.MultipleObjectsReturned):
            pass


###############################################################


class PersonKeyValueQuerySet(CustomQuerySet):
    def key_filter(self, key):
        qs = self.filter(
            models.Q(key__slug__iexact=key) | models.Q(key__verbose_name__iexact=key)
        )
        return qs.distinct()

    def lookup_filter(self, key, person=None):
        qs = self.active()
        if person is not None:
            qs = qs.filter(person=person)
        return qs.key_filter(key)

    def lookup(self, key, person=None):
        from .models import PersonKeyValue

        try:
            return self.lookup_filter(key, person).get()
        except (PersonKeyValue.DoesNotExist, PersonKeyValue.MultipleObjectsReturned):
            pass


###############################################################
