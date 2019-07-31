"""
Since many of these signals are for bidirectional updates,
An ephemeral ``_directory_directory_sync_signal`` attribute is used to prevent
circular signal handling.
"""
################################################################

from . import conf

SYNC_SLUGS = conf.get("signals:entrytypes-personflags")


def should_sync(slug):
    return "__all__" in SYNC_SLUGS or slug in SYNC_SLUGS


################################################################


def personflag_pre_save_to_entrytype(sender, instance, raw, **kwargs):
    """
    When a personflag is created, or has it's name changed,
    update the corresponding entrytype.

    Caution must be taken in this direction, because there are
    potentially many personflags we do not want as entrytypes.
    """
    if raw:
        return  # do not change other fields in this case.
    if getattr(instance, "_directory_sync_signal", False):
        return

    from .models import EntryType
    from people.models import PersonFlag

    if not should_sync(instance.slug):
        return

    if EntryType.objects.filter(slug=instance.slug).exists():
        # existing entrytype with the same slug?  Bail now!
        return
    # everything up to here is a sanity pre-check...

    entrytype = EntryType()
    if instance.pk is not None:
        # there is an old personflag, and the new entrytype does not already exist.
        old_personflag = PersonFlag.objects.get(pk=instance.pk)
        try:
            entrytype = EntryType.objects.get(slug=old_personflag.slug)
        except EntryType.DoesNotExist:
            # Nothing to synchronize -- not an existing entrytype.
            return

    entrytype.active = instance.active
    entrytype.slug = instance.slug
    entrytype.verbose_name = instance.verbose_name
    entrytype.verbose_name_plural = instance.verbose_name
    entrytype._directory_sync_signal = True
    entrytype.save()


################################################################


def personflag_post_delete_entrytype_delete(sender, instance, **kwargs):
    """
    When a personflag is deleted, and there is a corresponding
    entrytype, delete the entrytype also.

    Caution must be taken in this direction, because there are
    potentially many personflags we do not want as entrytypes.
    """
    if not should_sync(instance.slug):
        return
    from .models import EntryType

    try:
        entrytype = EntryType.objects.get(slug=instance.slug)
    except EntryType.DoesNotExist:
        return

    entrytype.delete()


################################################################


def entrytype_pre_save_to_personflag(sender, instance, raw, **kwargs):
    """
    When a entrytype is created, or has it's name changed,
    update the corresponding personflag.
    """
    if raw:
        return  # do not change other fields in this case.
    if getattr(instance, "_directory_sync_signal", False):
        return

    if not should_sync(instance.slug):
        return

    from people.models import PersonFlag
    from .models import EntryType

    if PersonFlag.objects.filter(slug=instance.slug).exists():
        # existing flag with the same slug?  Bail now!
        return
    # everything up to here is a sanity pre-check...

    personflag = PersonFlag()
    if instance.pk is not None:
        # there is an old entrytype, and the new personflag does not already exist.
        old_entrytype = EntryType.objects.get(pk=instance.pk)
        try:
            personflag = PersonFlag.objects.get(slug=old_entrytype.slug)
        except PersonFlag.DoesNotExist:
            pass

    personflag.active = instance.active
    personflag.slug = instance.slug
    personflag.verbose_name = instance.verbose_name
    personflag._directory_sync_signal = True
    personflag.save()


################################################################


def entrytype_post_delete_personflag_delete(sender, instance, **kwargs):
    """
    When a entrytype is deleted, and there is a corresponding
    personflag, delete the personflag also.
    """
    if not should_sync(instance.slug):
        return
    from people.models import PersonFlag

    try:
        personflag = PersonFlag.objects.get(slug=instance.slug)
    except PersonFlag.DoesNotExist:
        return

    personflag.delete()


################################################################


def person_flags_m2m_changed_handler(
    sender, instance, action, reverse, model, pk_set, **kwargs
):
    """
    Push person flag changes to corresponding directory entries, if any.
    """
    if getattr(instance, "_directory_sync_signal", False):
        return
    person = instance

    if action not in ["post_add", "post_remove", "pre_clear"]:
        return

    from .models import EntryType, DirectoryEntry
    from people.models import PersonFlag

    slug_list = []
    if pk_set is not None:
        slug_list = PersonFlag.objects.filter(pk__in=pk_set).values_list(
            "slug", flat=True
        )
    if action == "pre_clear":
        slug_list = person.flags.all().values_list("slug", flat=True)

    slug_list = [slug for slug in slug_list if should_sync(slug)]

    person._directory_sync_signal = True
    if action in ["pre_clear", "post_remove"]:
        directoryentry_qs = person.directoryentry_set.filter(
            active=True, type__slug__in=slug_list
        )
        directoryentry_qs.update(active=False)

    if action == "post_add":
        entrytype_slugs = EntryType.objects.slug_list()
        for slug in slug_list:
            if slug not in entrytype_slugs:
                continue
            entrytype = EntryType.objects.get(slug=slug)
            entry, created = DirectoryEntry.objects.get_or_create(
                type=entrytype, person=person
            )
            if not entry.active:
                entry.active = True
                entry.save()


################################################################


def directoryentry_pre_save(sender, instance, raw, **kwargs):
    """
    When a directoryentry is created, or updated;
    add or change the corresponding personflag to the person.
    """
    if raw:
        return  # do not change other fields in this case.
    if getattr(instance.person, "_directory_sync_signal", False):
        return

    from people.models import PersonFlag
    from .models import DirectoryEntry

    instance.person._directory_sync_signal = True

    if instance.pk is not None:
        # there is an old entry, has the type changed?
        old_entry = DirectoryEntry.objects.get(pk=instance.pk)
        if old_entry.type == instance.type:
            # nothing has changed for our purposes.
            return
        # remove old corresponding flag.
        if should_sync(old_entry.type.slug):
            old_flag = PersonFlag.objects.get(slug=old_entry.type.slug)
            instance.person.flags.remove(old_flag)

    # add new corresponding flag.
    if should_sync(instance.type.slug) and instance.active:
        flag = PersonFlag.objects.get(slug=instance.type.slug)
        instance.person.flags.add(flag)


################################################################


def directoryentry_post_delete(sender, instance, **kwargs):
    """
    When a entrytype is deleted, and there is a corresponding
    personflag, delete the personflag also.
    """
    if not should_sync(instance.type.slug):
        return
    from people.models import PersonFlag

    try:
        old_flag = PersonFlag.objects.get(slug=instance.type.slug)
    except PersonFlag.DoesNotExist:
        return

    instance.person._directory_sync_signal = True
    instance.person.flags.remove(old_flag)


################################################################
