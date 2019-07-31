"""
Managers for contacts.  A contact is a person and all of their associated information,
e.g., phone numbers, addresses, etc.
"""
#######################
from __future__ import print_function, unicode_literals

#######################
import hashlib
import random
import re
from importlib import import_module

from django.db import models

from . import conf, handlers
from .querysets import BaseContactInfoQuerySet, PersonFlagQuerySet, PersonQuerySet

DEFAULT_CONFIRM_SUBJECT_TEMPLATE = "people/email/confirm_subject.txt"
DEFAULT_CONFIRM_BODY_TEMPLATE = "people/email/confirm_body.txt"

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


#######################################################################


class PersonFlagManager(CustomQuerySetManager):
    """
    Manager for PersonFlag objects
    """

    queryset_class = PersonFlagQuerySet


PersonFlagManager = PersonFlagManager.from_queryset(PersonFlagQuerySet)

#######################################################################


class PersonManager(CustomQuerySetManager):
    """
    Manager for person records
    """

    queryset_class = PersonQuerySet

    def guess_name_helper(self, cn, given_name=None, sn=None):
        """
        Strictly a helper function, used when creating new users.
        This function does whitespace and puncuation normalization, and then
        calls the configured helper funciton (see conf.py, 'name_guess:function').
        Use this when not all name info is authoritive.
        Returns a dictionary of cn, sn, given_name values (best guess).
        """
        # do whitespace + puncuation normalization:
        if "." in cn:
            cn = cn.replace(".", ". ")
        if cn is not None:
            cn = " ".join(cn.split()).strip()
        if sn is not None:
            sn = " ".join(sn.split()).strip()
        if given_name is not None:
            given_name = " ".join(given_name.split()).strip()

        # call the helper
        f_callable_or_string = conf.get("name_guess:function")
        if f_callable_or_string is None:
            return dict(cn=cn, given_name=given_name, sn=sn)  # not configured.

        if callable(f_callable_or_string):
            f_callable = f_callable_or_string
        else:
            mod_name, f_name = f_callable_or_string.rsplit(".", 1)
            f_callable = getattr(import_module(mod_name), f_name)
        return f_callable(cn, given_name, sn)

    def get_by_username(self, username, **kwargs):
        return self.get(username=username, **kwargs)

    def get_by_user(self, user, **kwargs):
        return self.get_by_username(user.username, **kwargs)

    def create_from_user(
        self, user, flags=[], flags_are_slugs=False, guess_names=False
    ):
        """
        Create a new Person from the given User object.
        Return the person (the person will be saved).
        """
        if guess_names:
            names = self.guess_name_helper(user.get_full_name())
        else:
            names = dict(
                cn=user.get_full_name(), sn=user.last_name, given_name=user.first_name
            )

        obj = self.create(username=user.username, **names)
        if flags:
            for flag in flags:
                if flags_are_slugs:
                    obj.add_flag_by_name(flag)
                else:
                    obj.flags.add(flag)
            obj.save()  # update m2m
        return obj

    def get_or_create_from_user(
        self, user, flags=[], flags_are_slugs=False, guess_names=False
    ):
        """
        Get or create, with defaults from the user object.
        flags is *only* used if the object is created.
        """
        if guess_names:
            names = self.guess_name_helper(user.get_full_name())
        else:
            names = dict(
                cn=user.get_full_name(), sn=user.last_name, given_name=user.first_name
            )
        obj, created = self.get_or_create(username=user.username, defaults=names)
        if created and user.email:
            # create EmailAddress -- only when person is created.
            obj.add_email(user.email, conf.get("default_contact_info_type"))
        if created and flags:
            for flag in flags:
                if flags_are_slugs:
                    obj.add_flag_by_name(flag)
                else:
                    obj.flags.add(flag)
            obj.save()  # update m2m
        return obj, created

    def get_by_email(self, address, **kwargs):
        """
        Get a person by email address.
        This can throw all of the usual exceptions.
        **kwargs are applied against the EmailAddress lookup.
        """
        from .models import EmailAddress

        return EmailAddress.objects.get(address__iexact=address, **kwargs).person

    def get_or_create_by_email(
        self,
        address,
        person_defaults,
        default_type_slug=conf.get("default_contact_info_type"),
        extra_filters={},
        flags=[],
        flags_are_slugs=False,
        guess_names=False,
    ):
        """
        Get_by_email.  If there is none, create a new person
        extra_filters are applied against the email address lookup.
        (Use person__ if necessary).
        """
        created_flag = False
        try:
            person = self.get_by_email(address, **extra_filters)
        except EmailAddress.DoesNotExist:
            if guess_names and "cn" in person_defaults:
                if "sn" not in person_defaults:
                    person_defaults["sn"] = None
                if "given_name" not in person_defaults:
                    person_defaults["given_name"] = None
                person_defaults.update(
                    self.guess_name_helper(
                        person_defaults["cn"],
                        sn=person_defaults["sn"],
                        given_name=person_defaults["given_name"],
                    )
                )

            for field in ["cn", "sn", "given_name"]:
                if field not in person_defaults:
                    assert False, "required fields are not in person_defaults"

            created_flag = True
            person = Person(**person_defaults)
            person.save()
            person.add_email(address, default_type_slug)
            if flags:
                for flag in flags:
                    if flags_are_slugs:
                        person.add_flag_by_name(flag)
                    else:
                        person.flags.add(flag)
                person.save()  # update m2m

        return person, created_flag


PersonManager = PersonManager.from_queryset(PersonQuerySet)

###############################################################


class BaseContactInfoManager(CustomQuerySetManager):
    """
    Manager for ContactInfo
    """

    queryset_class = BaseContactInfoQuerySet


BaseContactInfoManager = BaseContactInfoManager.from_queryset(BaseContactInfoQuerySet)

###############################################################


class EmailConfirmationManager(CustomQuerySetManager):

    SHA1_RE = re.compile("^[a-f0-9]{40}$")

    def start_verification(
        self,
        email,
        site=None,
        send_email=True,
        redirect_url=None,
        delete_unverified=False,
        subject_template=DEFAULT_CONFIRM_SUBJECT_TEMPLATE,
        body_template=DEFAULT_CONFIRM_BODY_TEMPLATE,
        extra_email_context=None,
    ):
        """
        Begin the verification process
        """
        salt = "{}".format(random.random())[2:8]
        value = salt + "{}".format(email)
        key = hashlib.sha1(value.encode("utf-8")).hexdigest()

        verification, created = self.get_or_create(
            email=email, defaults={"key": key, "redirect_url": redirect_url}
        )
        if created and not verification.active:
            verification.active = True
            verification.save()

        if send_email:
            verification.send_email(
                site=site,
                subject_template=subject_template,
                body_template=body_template,
                extra_email_context=extra_email_context,
            )

    def verify(key):
        """
        Returns the pair None, None if things don't work out,
        otherwise returns the  email, redirect_url pair

        This is not really used in the current implementation,
        see the object set_verified method
        """
        if not self.SHA1_RE.search(key):
            return None, None
        try:
            verification = self.get(active=True, verification_key=key)
        except self.model.DoesNotExist:
            return None, None
        if not verification.is_valid():
            return None, None

        verification.set_verified(set_email=True)
        return verification.email, verification.redirect_url

    def delete_expired(self):
        """
        A troublesome user/email can be dealt with by setting
        the email_send_time to None, which will never delete.

        EmailAddresses & People will only be deleted when
        the verify record has the delete_unverified flag set
        and the email is marked as unverified.
        """
        # note: may need  a try...except self.model.DoesNotExist
        for verify in self.all():
            if not verify.is_valid() and verify.email_send_time is not None:
                delete = verify.delete_unverified
                if delete:
                    email = verify.email
                verify.delete()
                if delete and not email.verified:
                    person = email.person
                    email.delete()
                    person.delete()


###############################################################
