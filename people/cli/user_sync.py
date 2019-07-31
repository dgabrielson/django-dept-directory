HELP_TEXT = "Synchronize information from Person objects to User objects"
DJANGO_COMMAND = "main"
USE_ARGPARSE = True
OPTION_LIST = (
    (
        ["--update-person"],
        dict(
            action="store_true",
            help="Update person names from corresponding user objects",
        ),
    ),
    (
        ["--update-user"],
        dict(
            action="store_true",
            help="Update user names from corresponding person objects (default)",
        ),
    ),
)

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from .. import conf, handlers
from ..models import Person, PersonFlag


def update_person_from_user(person, user):
    """
    user -> person (update person)
    """
    if conf.get("sync:person:user:create-delete"):
        handlers.user_post_save_create_person(__name__, user, False, person is None)

    if conf.get("sync:person:user-name"):
        handlers.user_post_save_name_to_person(__name__, user, False, False)

    if conf.get("sync:person:user-email"):
        handlers.user_post_save_email_to_person(__name__, user, False, False)

    if conf.get("sync:person-flags:user-groups"):
        User = get_user_model()
        pk_set = list(user.groups.all().values_list("pk", flat=True))
        handlers.user_groups_m2m_changed_handler(
            __name__, user, "post_add", False, User, pk_set
        )


def update_flags_from_groups():
    """
    Groups -> PersonFlags
    """
    if conf.get("sync:person-flags:user-groups"):
        for group in Group.objects.all():
            handlers.group_pre_save_to_personflag(__name__, group, False)


def update_groups_from_flags():
    """
    PersonFlags -> Groups.
    """
    if conf.get("sync:person-flags:user-groups"):
        for personflag in PersonFlag.objects.all():
            handlers.personflag_pre_save_to_group(__name__, personflag, False)


def update_user_from_person(person, user):
    """
    person -> user (update user)
    """
    if conf.get("sync:person:user:create-delete"):
        handlers.person_post_save_create_user(__name__, person, False, user is None)

    if conf.get("sync:person:user-name"):
        handlers.person_post_save_name_to_user(__name__, person, False, False)

    if conf.get("sync:person:user-email"):
        emailaddress_qs = person.emailaddress_set.active()
        if emailaddress_qs:
            handlers.emailaddress_post_save_email_to_user(
                __name__, emailaddress_qs[0], False, False
            )

    if conf.get("sync:person-flags:user-groups"):
        pk_set = list(person.flags.all().values_list("pk", flat=True))
        handlers.person_flags_m2m_changed_handler(
            __name__, person, "post_add", False, Person, pk_set
        )


def main(options, args):

    if options["update_user"] and options["update_person"]:
        print("You cannot update both users and people at the same time")
        return
    if options["update_user"] and not options["update_person"]:
        update = update_user_from_person
    if not options["update_user"] and options["update_person"]:
        update = update_person_from_user
    if not options["update_user"] and not options["update_person"]:
        # the default
        update = update_user_from_person

    if args:
        print("This command takes no arguments.")
        return

    quiet = options["verbosity"] == "0"

    User = get_user_model()

    if update == update_user_from_person:
        update_groups_from_flags()
        for person in Person.objects.all():
            try:
                user = person.get_user()
            except User.DoesNotExist:
                user = None
            flag = update(person, user)

    if update == update_person_from_user:
        update_flags_from_groups()
        for user in User.objects.all():
            try:
                person = Person.objects.get_by_user(user)
            except Person.DoesNotExist:
                person = None
            flag = update(person, user)

    ###
