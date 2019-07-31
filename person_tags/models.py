"""
Models for the person_tags.


Example Usages:
    * page of research interests.
"""
from __future__ import print_function, unicode_literals

import os

from django.db import models
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from people.models import Person

from . import conf

#######################################################################


class CustomQuerySetManager(models.Manager):
    """
    Custom Manager for an arbitrary model, just a wrapper for returning
    a custom QuerySet
    """

    queryset_class = models.query.QuerySet

    def get_queryset(self):
        """
        Return the custom QuerySet
        """
        return self.queryset_class(self.model)


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


class PersonTagQuerySet(CustomQuerySet):
    """
    Defines person_list and tag_list
    """

    def person_list(self):
        """
        Return a list of tagged people
        """
        pk_list = self.values_list("pk", flat=True)
        return PersonTaggedEntry.objects.get_people(tag__pk__in=pk_list)

    def tag_list(self):
        """
        Return a list of tags which are actually in use
        """
        pk_list = self.values_list("pk", flat=True)
        return PersonTaggedEntry.objects.get_tags(tag__pk__in=pk_list)


class PersonTagManager(CustomQuerySetManager):
    queryset_class = PersonTagQuerySet


PersonTagManager = PersonTagManager.from_queryset(PersonTagQuerySet)


@python_2_unicode_compatible
class PersonTag(models.Model):

    active = models.BooleanField(default=True)
    created = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name="creation time"
    )
    modified = models.DateTimeField(
        auto_now=True, editable=False, verbose_name="last modification time"
    )

    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL fragment")
    tag = models.CharField(
        max_length=255,
        help_text="A word or short phrase (only a few words) is best. Do not use capitals except in proper names.",
    )

    objects = PersonTagManager()

    class Meta:
        ordering = ["tag"]
        base_manager_name = "objects"

    def __str__(self):
        return self.tag

    def get_absolute_url(self):
        if self.groups.count() == 1:
            return reverse(
                "persontag-taggroup-detail", kwargs={"slug": self.groups.get().slug}
            )
        else:
            return reverse("persontag-tag-detail", kwargs={"slug": self.slug})

    @property
    def groups(self):
        """
        Returns a queryset of groups that this tag belongs to.
        """
        return TagGroup.objects.filter(tags=self).active()


#######################################################################


class PersonTaggedEntryQuerySet(CustomQuerySet):
    def get_people(self, **kwargs):
        """
        Given a person tag, return the list of people who have that tag.
        """
        qs = self.filter(active=True, **kwargs)
        pk_list = qs.values_list("person", flat=True).distinct()
        # NB: DISTINCT required b/c directoryentry__active will
        #   cause people with multiple directory entries to occur
        #   multiple times.
        return Person.objects.filter(
            active=True,
            pk__in=pk_list,
            flags__slug="directory",
            directoryentry__active=True,
        ).distinct()

    def get_tags(self, **kwargs):
        """
        Given a person, return all associated tags.
        """
        qs = self.filter(active=True, **kwargs)
        pk_list = qs.values_list("tag", flat=True).distinct()
        return PersonTag.objects.filter(active=True, pk__in=pk_list)

    def default(self):
        """
        Get a default queryset
        """
        return self.filter(
            active=True,
            tag__active=True,
            person__active=True,
            person__flags__slug="directory",
        ).select_related("person", "tag")


class PersonTaggedEntryManager(CustomQuerySetManager):
    queryset_class = PersonTaggedEntryQuerySet


PersonTaggedEntryManager = PersonTaggedEntryManager.from_queryset(
    PersonTaggedEntryQuerySet
)


@python_2_unicode_compatible
class PersonTaggedEntry(models.Model):
    """
    Essentially managing the Many to many relationship manually, with
    optional ordering.
    """

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
    )
    tag = models.ForeignKey(
        PersonTag, on_delete=models.CASCADE, limit_choices_to={"active": True}
    )
    ordering = models.PositiveSmallIntegerField(default=10)

    objects = PersonTaggedEntryManager()

    class Meta:
        ordering = ["person", "ordering", "tag"]
        verbose_name_plural = "person tagged entries"
        unique_together = [["person", "tag"]]
        base_manager_name = "objects"

    def __str__(self):
        return "{}".format(self.tag)


#######################################################################


class TagGroupQuerySet(CustomQuerySet):
    """
    Custom QuerySet for TagGroups.
    """


class TagGroupManager(CustomQuerySetManager):
    queryset_class = TagGroupQuerySet


TagGroupManager = TagGroupManager.from_queryset(TagGroupQuerySet)


@python_2_unicode_compatible
class TagGroup(models.Model):
    """
    Class for tag groups
    """

    active = models.BooleanField(default=True)
    created = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name="creation time"
    )
    modified = models.DateTimeField(
        auto_now=True, editable=False, verbose_name="last modification time"
    )

    name = models.CharField(max_length=128)
    short_name = models.CharField(max_length=64, blank=True)
    slug = models.SlugField(max_length=32, unique=True, verbose_name="URL fragment")

    description = models.TextField(blank=True)

    tags = models.ManyToManyField(PersonTag, blank=True)

    objects = TagGroupManager()

    class Meta:
        ordering = ["name"]
        base_manager_name = "objects"

    def __str__(self):
        return self.short_name or self.name

    def get_absolute_url(self):
        """
        Return the url
        """
        return reverse("persontag-taggroup-detail", kwargs={"slug": self.slug})

    @property
    def people(self):
        """
        Return a queryset of people who have tags in this group.
        """
        return self.tags.person_list()
        tag_pk_list = self.tags.values_list("pk", flat=True)
        qs = PersonTaggedEntry.objects.filter(tag__pk__in=tag_pk_list)
        return qs.get_people()


#######################################################################


@python_2_unicode_compatible
class Asset(models.Model):
    """
    A file asset for a shout.
    """

    active = models.BooleanField(default=True)
    created = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name="creation time"
    )
    modified = models.DateTimeField(
        auto_now=True, editable=False, verbose_name="last modification time"
    )
    taggroup = models.ForeignKey(TagGroup, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to=conf.get("upload_to"), storage=conf.get("storage")
    )
    description = models.CharField(max_length=250, blank=True)

    def get_absolute_url(self):
        return self.file.url

    get_absolute_url.short_description = "url"

    def __str__(self):
        name = os.path.basename(self.file.name)
        if self.description:
            name += ": " + self.description
        return name


###############################################################
#
