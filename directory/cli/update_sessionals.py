"""
Synchronize the list of instructors against the list of academic staff,
and update the list of sessional instructors appropriately for active courses.
"""
from __future__ import print_function, unicode_literals

from classes.models import Section
from directory import conf
from directory.models import DirectoryEntry
from people.models import Person

#############################################################

DJANGO_COMMAND = "main"
HELP_TEXT = __doc__.strip()
USE_ARGPARSE = True
OPTION_LIST = (
    (["-r", "--role"], dict(action="store_true", help="Use course role times also")),
)

#############################################################


def get_instructor_keys(section_list, use_role):

    if use_role:
        from gradebook import conf as gradebook_conf
        from gradebook.models import Role, Ledger, LedgerViewport
        from django.utils.timezone import now

        # convert section_list to viewport_list...
        viewport_from_section = gradebook_conf.get("viewport_from_section")
        viewport_list = [
            viewport_from_section(Ledger, LedgerViewport, section)
            for section in section_list
        ]

        instructor_pks = set(
            Role.objects.filter(
                viewport__in=viewport_list,
                role__in=["in", "co"],
                dtstart__lte=now(),
                dtend__gte=now(),
            ).values_list("person", flat=True)
        )
    else:
        instructor_list = set(section_list.values_list("instructor", flat=True))
        addl = set(section_list.values_list("additional_instructors__id", flat=True))
        if None in addl:
            addl.remove(None)
        instructor_pks = instructor_list.union(addl)

    return instructor_pks


def main(options, args):
    """
    options and args are not used.
    """
    config = conf.get("update_sessionals")

    section_list = Section.objects.get_current().filter(instructor__isnull=False)
    # exclude configured section types
    section_type_exclude = config.get("section:type:exclude")
    if section_type_exclude:
        section_list = section_list.exclude(section_type__in=section_type_exclude)

    instructor_pks = get_instructor_keys(section_list, options["role"])
    academic_slug_list = config.get("academic:type:slug_list", [])
    sessional_slug_list = config.get("sessional:type:slug_list", [])
    all_types_slug_list = academic_slug_list + sessional_slug_list
    cn_blacklist = config.get("cn:blacklist", [])

    # the type slugs should be more configurable, somehow.
    entry_list = DirectoryEntry.objects.active().filter(
        type__slug__in=all_types_slug_list
    )
    academic_pks = set(
        entry_list.filter(type__slug__in=academic_slug_list).values_list(
            "person", flat=True
        )
    )
    sessional_list = entry_list.filter(type__slug__in=sessional_slug_list)
    sessional_pks = set(sessional_list.values_list("person", flat=True))
    non_academic_pks = instructor_pks.difference(academic_pks)

    remove_pks = sessional_pks.difference(non_academic_pks)
    add_pks = non_academic_pks.difference(sessional_pks)

    # this would be more efficient with a queryset update, but would give
    #   less feedback.
    for entry in sessional_list.filter(person__pk__in=remove_pks):
        print("Removing {}".format(entry))
        entry.active = False
        entry.save()

    # Try and find non-active sessional entries.
    section_set = set(section_list)
    all_sessional_list = DirectoryEntry.objects.filter(
        type__slug__in=sessional_slug_list
    )
    for entry in all_sessional_list.filter(person__pk__in=add_pks):
        section_entry_set = set(entry.person.section_set.current_or_future())
        addl_section_entry_set = set(
            entry.person.additional_instructor_section.current_or_future()
        )
        entry_section_set = section_entry_set.union(addl_section_entry_set)

        # only reactivate for *current* or *future* sections!
        if not section_set.isdisjoint(entry_section_set):
            print("Reactivating {}".format(entry))
            entry.active = True
            entry.save()
        add_pks.remove(entry.person.pk)

    # Now complain about the remainder:
    for person in Person.objects.filter(pk__in=add_pks).exclude(cn__in=cn_blacklist):
        if not person.active:
            person.active = True
            person.save()
            print("Reactivated person {}".format(person))
        print("*** need directory entry for sessional instructor: {}".format(person))
        person.add_flag_by_name("directory")
