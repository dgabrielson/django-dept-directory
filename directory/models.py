"""
Models for the directory.

Directory pages are summaries of people that have specific information or organization.

Example Usages:
    * page of department members, by type
    * page of faces
    * page of research interests.
"""
###############
from __future__ import print_function, unicode_literals

from importlib import import_module

###############
from django.apps import apps
from django.db import models
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from people.models import Person

from . import PhoneNumberField, conf

mugshot_uploadto = conf.get("mugshot_path")
office_modelname = conf.get("office_model")  # e.g. 'places.Office'

######################################################################


class CustomQuerySetManager(models.Manager):
    """
    Custom Manager for an arbitrary model, just a wrapper for returning
    a custom QuerySet
    """

    queryset_class = models.query.QuerySet
    always_select_related = None
    always_prefetch_related = None

    # use always_select_related when the "{}".format()/str() method for a model
    #   pull foreign keys.

    def get_queryset(self):
        """
        Return the custom QuerySet
        """
        queryset = self.queryset_class(self.model)
        if self.always_select_related is not None:
            queryset = queryset.select_related(*self.always_select_related)
        if self.always_prefetch_related is not None:
            queryset = queryset.prefetch_related(*self.always_prefetch_related)
        return queryset


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
#######################################################################
#######################################################################


class EntryTypeQuerySet(CustomQuerySet):
    """
    Defines person_list and tag_list
    """

    def slug_list(self):
        """
        Return a list of tagged people
        """
        return self.values_list("slug", flat=True)


class EntryTypeManager(CustomQuerySetManager):
    queryset_class = EntryTypeQuerySet


EntryTypeManager = EntryTypeManager.from_queryset(EntryTypeQuerySet)


@python_2_unicode_compatible
class EntryType(models.Model):
    """
    Different Types of People.

    Examples: Academic Staff, Senior Scholars, Graduate Students, Undergraduate Students.
    """

    active = models.BooleanField(default=True)
    created = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name="creation time"
    )
    modified = models.DateTimeField(
        auto_now=True, editable=False, verbose_name="last modification time"
    )

    slug = models.SlugField(max_length=64, unique=True)
    verbose_name = models.CharField(max_length=64)
    verbose_name_plural = models.CharField(max_length=64)
    ordering = models.PositiveSmallIntegerField(default=10)

    objects = EntryTypeManager()

    class Meta:
        ordering = ["ordering", "verbose_name"]
        base_manager_name = "objects"

    def __str__(self):
        return self.verbose_name


#######################################################################


class DirectoryEntryQuerySet(CustomQuerySet):
    """
    """

    def active(self, **kwargs):
        return self.filter(active=True, person__active=True)

    def default_list(self, **kwargs):
        """
        Returns a flat query set of directory entries.
        This applies a default set of filters.
        """
        return self.filter(
            active=True, person__active=True, type__active=True, **kwargs
        ).distinct()

    def offices_only(self):
        """
        Restricts the current queryset to only entries that have an office
        """
        return self.filter(office__isnull=False)

    def distinct_offices(self, **kwargs):
        """
        Returns a list of distinct offices.
        Typically used with person.directoryentry_set in a template,
        e.g.,
        {% for office in person.directoryentry_set.distinct_offices %}
            ...
        {% endfor %}
        """
        pk_list = (
            self.filter(active=True)
            .exclude(office__isnull=True)
            .distinct()
            .values_list("office")
        )
        office_model = apps.get_model(*office_modelname.split("."))
        return office_model.objects.filter(pk__in=pk_list)

    def person_list(self, **kwargs):
        """
        Returns a list of distinct people with one or more active
        directory entries.
        ``kwargs``, if given, are additional filters on the DirectoryEntries.
        """
        pk_list = self.filter(active=True, **kwargs).values_list("person")
        return Person.objects.filter(active=True, pk__in=pk_list)

    def type_slug_list(self):
        pk_list = self.values_list("type", flat=True)
        type_list = EntryType.objects.filter(pk__in=pk_list)
        return type_list.slug_list()


class DirectoryEntryManager(CustomQuerySetManager):
    queryset_class = DirectoryEntryQuerySet
    always_select_related = ["type", "person", "office"]
    always_prefetch_related = ["person__phonenumber_set", "person__emailaddress_set"]


DirectoryEntryManager = DirectoryEntryManager.from_queryset(DirectoryEntryQuerySet)


@python_2_unicode_compatible
class DirectoryEntry(models.Model):

    active = models.BooleanField(default=True)
    created = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name="creation time"
    )
    modified = models.DateTimeField(
        auto_now=True, editable=False, verbose_name="last modification time"
    )

    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        limit_choices_to={"active": True, "flags__slug": "directory"},
        help_text='Only people with the "directory" flag are shown',
    )

    type = models.ForeignKey(EntryType, on_delete=models.PROTECT)
    description = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="(Optional) only used on personal pages to distinguish multiple offices.",
    )

    title = models.CharField(
        max_length=64,
        blank=True,
        help_text="(Optional) if not given, the person's title will be used.",
    )
    url = models.CharField(
        max_length=64,
        blank=True,
        help_text="(Optional) if not given, the person's url will be used.",
        verbose_name="URL",
    )
    phone_number = PhoneNumberField(
        blank=True,
        default="",
        help_text="(Optional) if not given, the office's phone number will be used.",
    )
    office = models.ForeignKey(
        office_modelname, on_delete=models.SET_NULL, null=True, blank=True
    )
    mugshot = models.ImageField(
        upload_to=mugshot_uploadto,
        max_length=512,
        null=True,
        blank=True,
        help_text="(Optional) a photo for the visual directory.",
    )
    note = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="(Optional) a short note about e.g., being on leave.",
    )

    ordering = models.PositiveSmallIntegerField(default=100)

    objects = DirectoryEntryManager()

    class Meta:
        ordering = ["type", "ordering", "person"]
        verbose_name_plural = "directory entries"
        unique_together = ["person", "type"]
        base_manager_name = "objects"

    def __str__(self):
        return "{}".format(self.person)

    def get_absolute_url(self):
        if self.url:
            return self.url
        get_absolute_url = getattr(self.person, "get_absolute_url", None)
        if get_absolute_url is not None:
            return get_absolute_url()


#
