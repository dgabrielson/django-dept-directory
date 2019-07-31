# -*- coding: utf-8 -*-
"""
Places, Locations, etc.
"""
###############
from __future__ import print_function, unicode_literals

import operator

###############
from functools import reduce

from directory import PhoneNumberField
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

# Create your models here.


class Room_Manager(models.Manager):
    """
    Custom methods:
    
    * search
    * active
    """

    def active(self):
        """"Room.objects.active() -> <QuerySet>
        
        Return a queryset of active rooms.
        """
        return self.filter(active=True)

    def search(self, *criteria):
        """Room.objects.search(*criteria) -> <QuerySet>
        Magic search for rooms.
        This is heavily modelled after the way the Django Admin handles
        search queries.
        See: django.contrib.admin.views.main.py:ChangeList.get_query_set
        """
        if len(criteria) == 0:
            assert False, "Supply search criteria"

        search_fields = ["number", "building"]
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


@python_2_unicode_compatible
class Room(models.Model):
    """
    Base class for rooms.
    """

    active = models.BooleanField(default=True)
    created = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name="creation time"
    )
    modified = models.DateTimeField(
        auto_now=True, editable=False, verbose_name="last modification time"
    )

    slug = models.SlugField(max_length=64, unique=True)
    number = models.CharField(
        max_length=32, help_text="These are room labels – not always numeric"
    )
    building = models.CharField(
        max_length=64,
        help_text='Use "-special" to display only the number label for the room',
    )
    note = models.CharField(
        max_length=128,
        blank=True,
        help_text="A key serial number, room combination, i>clicker frequency, etc.",
    )

    objects = Room_Manager()

    class Meta:
        ordering = ["building", "number"]
        unique_together = [["number", "building"]]

    def __str__(self):
        if self.building != "-special":
            return self.number + " " + self.building
        return self.number


class ClassRoom_Manager(Room_Manager):
    def TBA(self):
        """
        Return the TBA room.  Create it if it doesn't exist.
        """
        obj, flag = self.get_or_create(number="TBA", building="-special", slug="tba")
        return obj

    def Online(self):
        """
        Return the ONLINE room.  Create it if it doesn't exist.
        """
        obj, flag = self.get_or_create(
            number="Online", building="-special", slug="online"
        )
        return obj


class ClassRoom(Room):
    """
    If a room might *ever* have classes scheduled in it, it is a classroom.
    """

    capacity = models.PositiveSmallIntegerField(null=True, blank=True)

    objects = ClassRoom_Manager()


class Office(Room):
    """
    Offices have phone numbers.
    """

    phone_number = PhoneNumberField(blank=True)

    objects = Room_Manager()
