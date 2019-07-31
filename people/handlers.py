"""
Signal handlers for the people app.
"""
#######################
from __future__ import print_function, unicode_literals

from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.utils.text import slugify

from . import conf
from .utils import (
    get_person_user_pair,
    person2user_email,
    person2user_name,
    user2person_name,
)

#######################
################################################################

################################################################


def person_pre_save_set_slug(sender, instance, raw, **kwargs):
    """
    Set a unique slug, if there is no slug.
    TODO: determine how much of this is replaced by django-autoslug.
    """
    if raw:
        return  # do not change other fields in this case.

    if instance.slug:
        return  # do nothing.

    slug = slugify(instance.cn)
    model = instance.__class__
    n = 1
    while True:
        qs = model.objects.filter(slug__exact=slug)
        if not qs.exists():
            break
        slug = slugify(instance.cn) + "-{0}".format(n)
        n += 1
    instance.slug = slug


################################################################


def person_post_save_name_to_user(sender, instance, raw, created, **kwargs):
    """
    When a person's name changes, and there is a corresponding
    user, change the user's name also.
    """
    if raw:
        return  # do not change other fields in this case.

    person, user = get_person_user_pair(person=instance)
    if user is None:
        return
    if person2user_name(person, user):
        user.save()


################################################################


def person_post_save_create_user(sender, instance, raw, created, **kwargs):
    """
    When a person is created, and there is a username set, 
    create the user also.
    """
    if raw:
        return  # do not change other fields in this case.

    person, user = get_person_user_pair(person=instance)
    if not person.username:
        return
    if user is not None:
        return

    UserModel = get_user_model()
    user = UserModel(username=person.username)
    b1 = person2user_name(person, user)
    b2 = person2user_email(person, user)
    if b1 or b2:
        user.save()


################################################################


def person_post_delete_user_delete(sender, instance, **kwargs):
    """
    When a person's is going to be deleted, and there is a corresponding
    user, delete the user also.
    """
    person, user = get_person_user_pair(person=instance)
    if user is None:
        return

    user.delete()


################################################################


def user_post_save_name_to_person(sender, instance, raw, created, **kwargs):
    """
    When a user's name changes, and there is a corresponding
    person, change the person's name also.
    """
    if raw:
        return  # do not change other fields in this case.

    from django.contrib.auth.models import AnonymousUser

    if isinstance(instance, AnonymousUser):
        return

    person, user = get_person_user_pair(user=instance)
    if person is None:
        return

    if user2person_name(person, user):
        person.save()


################################################################


def user_post_save_email_to_person(sender, instance, raw, created, **kwargs):
    """
    When a user's email changes, and there is a corresponding
    person, update the person's email also.
    """
    if raw:
        return  # do not change other fields in this case.
    from django.contrib.auth.models import AnonymousUser

    if isinstance(instance, AnonymousUser):
        return
    if getattr(instance, "_sync_signal", False):
        return

    person, user = get_person_user_pair(user=instance)
    if person is None:
        return
    if not user.email:
        return

    done = False
    person.emailaddress_set.update(preferred=False)
    for e_addr in person.emailaddress_set.all():
        if e_addr.address == user.email:
            if not e_addr.active:
                e_addr.active = True
            if not e_addr.preferred:
                e_addr.preferred = True
            e_addr._sync_signal = True
            e_addr.save()
            done = True
    if not done:
        person.add_email(
            user.email, conf.get("default_contact_info_type"), preferred=True
        )


################################################################


def emailaddress_post_save_email_to_user(sender, instance, raw, created, **kwargs):
    """
    When a person's email changes, and there is a corresponding
    user, update the user's email also.
    """
    if raw:
        return  # do not change other fields in this case.
    if getattr(instance, "_sync_signal", False):
        return

    person, user = get_person_user_pair(person=instance.person)
    if user is None:
        return
    # really, only ever set the preferred email address to the user account

    if person2user_email(person, user):
        user._sync_signal = True
        user.save()


################################################################


def user_post_save_create_person(sender, instance, raw, created, **kwargs):
    """
    When a user is created, create a corresponding person.
    """
    if raw:
        return  # do not change other fields in this case.
    if not created:
        return  # existing field changes are handled elsewhere
    from django.contrib.auth.models import AnonymousUser

    if isinstance(instance, AnonymousUser):
        return

    person, user = get_person_user_pair(user=instance)
    if person is not None:
        return

    from .models import Person

    Person.objects.create_from_user(user)


################################################################


def user_post_delete_person_delete(sender, instance, **kwargs):
    """
    When a user is going to be deleted, and there is a corresponding
    person, delete the person also when configured; otherwise
    just clear the person's username.
    """
    from django.contrib.auth.models import AnonymousUser

    if isinstance(instance, AnonymousUser):
        return
    person, user = get_person_user_pair(user=instance)
    if person is None:
        return

    if conf.get("sync:person:user:create-delete:delete-person"):
        person.delete()
    else:
        person.username = None
        person.save()


################################################################


def personflag_pre_save_to_group(sender, instance, raw, **kwargs):
    """
    When a personflag is created, or has it's name changed,
    update the corresponding group.
    """
    if raw:
        return  # do not change other fields in this case.
    if getattr(instance, "_sync_signal", False):
        return

    from django.contrib.auth.models import Group
    from .models import PersonFlag

    new_name = "{}".format(instance.verbose_name)
    if Group.objects.filter(name=new_name).exists():
        # existing group with the new name?  Bail now!
        return
    # everything up to here is a sanity pre-check...

    group = Group()
    if instance.pk is not None:
        # there is an old personflag, and the new group does not already exist.
        old_personflag = PersonFlag.objects.get(pk=instance.pk)
        try:
            group = Group.objects.get(name=old_personflag.verbose_name)
        except Group.DoesNotExist:
            pass

    group.name = new_name
    group._sync_signal = True
    group.save()


################################################################


def personflag_post_delete_group_delete(sender, instance, **kwargs):
    """
    When a personflag is deleted, and there is a corresponding
    group, delete the group also.
    """
    from django.contrib.auth.models import Group

    try:
        group = Group.objects.get(name=instance.verbose_name)
    except Group.DoesNotExist:
        return

    group.delete()


################################################################


def group_pre_save_to_personflag(sender, instance, raw, **kwargs):
    """
    When a group is created, or has it's name changed,
    update the corresponding personflag.
    """
    if raw:
        return  # do not change other fields in this case.
    if getattr(instance, "_sync_signal", False):
        return

    from .models import PersonFlag
    from django.contrib.auth.models import Group

    new_name = "{}".format(instance.name)
    if PersonFlag.objects.filter(verbose_name=new_name).exists():
        # existing flag with the new name?  Bail now!
        return
    # everything up to here is a sanity pre-check...

    personflag = PersonFlag(slug=slugify(new_name))
    if instance.pk is not None:
        # there is an old group, and the new personflag does not already exist.
        old_group = Group.objects.get(pk=instance.pk)
        try:
            personflag = PersonFlag.objects.get(verbose_name=old_group.name)
        except PersonFlag.DoesNotExist:
            pass

    personflag.verbose_name = new_name
    personflag._sync_signal = True
    personflag.save()


################################################################


def group_post_delete_personflag_delete(sender, instance, **kwargs):
    """
    When a group is deleted, and there is a corresponding
    personflag, delete the personflag also.
    """
    from .models import PersonFlag

    try:
        personflag = PersonFlag.objects.get(verbose_name=instance.name)
    except PersonFlag.DoesNotExist:
        return

    personflag.delete()


################################################################


def person_flags_m2m_changed_handler(
    sender, instance, action, reverse, model, pk_set, **kwargs
):
    """
    Push person flag changes to user groups.
    """
    if getattr(instance, "_sync_signal", False):
        return
    person, user = get_person_user_pair(person=instance)
    if user is None:
        return
    if action not in ["post_add", "post_remove", "pre_clear"]:
        return

    from django.contrib.auth.models import Group
    from .models import PersonFlag

    name_list = []
    if pk_set is not None:
        name_list = PersonFlag.objects.filter(pk__in=pk_set).values_list(
            "verbose_name", flat=True
        )
    if action == "pre_clear":
        name_list = person.flags.all().values_list("verbose_name", flat=True)

    user._sync_signal = True
    if action in ["pre_clear", "post_remove"]:
        group_list = list(user.groups.filter(name__in=name_list))
        user.groups.remove(*group_list)

    if action == "post_add":
        group_list = []
        for name in name_list:
            group, created = Group.objects.get_or_create(name=name)
            group_list.append(group)
        user.groups.add(*group_list)


################################################################


def user_groups_m2m_changed_handler(
    sender, instance, action, reverse, model, pk_set, **kwargs
):
    """
    Push user group changes to person flags.
    """
    from django.contrib.auth.models import AnonymousUser

    if isinstance(instance, AnonymousUser):
        return
    if getattr(instance, "_sync_signal", False):
        return
    person, user = get_person_user_pair(user=instance)
    if person is None:
        return
    if action not in ["post_add", "post_remove", "pre_clear"]:
        return

    from django.contrib.auth.models import Group
    from .models import PersonFlag

    name_list = []
    if pk_set is not None:
        name_list = Group.objects.filter(pk__in=pk_set).values_list("name", flat=True)
    if action == "pre_clear":
        name_list = user.groups.all().values_list("name", flat=True)

    person._sync_signal = True
    if action in ["pre_clear", "post_remove"]:
        personflag_list = list(person.flags.filter(verbose_name__in=name_list))
        person.flags.remove(*personflag_list)

    if action == "post_add":
        personflag_list = []
        for name in name_list:
            slug = slugify(name)
            personflag, created = PersonFlag.objects.get_or_create(
                verbose_name=name, defaults={"slug": slug}
            )
            personflag_list.append(personflag)
        person.flags.add(*personflag_list)


################################################################
