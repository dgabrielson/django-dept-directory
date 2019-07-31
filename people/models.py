"""
Models for contacts.  A contact is a person and all of their associated information,
e.g., phone numbers, addresses, etc.
"""
###############
from __future__ import print_function, unicode_literals

###############
import datetime
import re
from importlib import import_module

from autoslug.fields import AutoSlugField
from directory import PhoneNumberField, PostalCodeField, RegionField
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.core import validators
from django.core.mail import EmailMessage
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible

from . import conf, handlers
from .managers import (
    DEFAULT_CONFIRM_BODY_TEMPLATE,
    DEFAULT_CONFIRM_SUBJECT_TEMPLATE,
    BaseContactInfoManager,
    EmailConfirmationManager,
    PersonFlagManager,
    PersonManager,
)
from .querysets import PersonKeyQuerySet, PersonKeyValueQuerySet

#######################################################################

PERSON_PERMALINK = conf.get("permalink")

#######################################################################


class PeopleBaseModel(models.Model):
    """
    An abstract base class.
    """

    active = models.BooleanField(default=True)
    created = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name="creation time"
    )
    modified = models.DateTimeField(
        auto_now=True, editable=False, verbose_name="last modification time"
    )

    class Meta:
        abstract = True


#######################################################################


@python_2_unicode_compatible
class PersonFlag(PeopleBaseModel):
    """
    Flags for differentating people.
    Typically these are used to filter Person choices as FK in other apps.

    Examples: student, advisor, committee member, graduate student,
        in directory, etc.
    """

    slug = AutoSlugField(max_length=64, populate_from="verbose_name", unique=True)
    verbose_name = models.CharField(max_length=64)

    objects = PersonFlagManager()

    class Meta:
        ordering = ["verbose_name"]
        base_manager_name = "objects"

    def __str__(self):
        return self.verbose_name


#######################################################################


@python_2_unicode_compatible
class Person(PeopleBaseModel):
    """
    A person.  Any known person goes here.
    """

    flags = models.ManyToManyField(PersonFlag, blank=True)

    cn = models.CharField(
        max_length=100,
        verbose_name="common name",
        blank=True,
        help_text="""This is how the person's name will appear in the site.
                                    Leave this blank to use given name + family name.
                                    """,
    )
    sn = models.CharField(
        max_length=64,
        verbose_name="family name",
        help_text="This will determine how this person gets sorted in lists or people.",
    )
    given_name = models.CharField(
        max_length=64,
        help_text="Typically how the person prefers to be addressed, informally.",
    )
    sync_name = models.BooleanField(
        default=True,
        verbose_name="sync name with user",
        help_text="Synchronize name information with corresponding user model",
    )
    title = models.CharField(
        max_length=64, blank=True, help_text="A personal title or job title."
    )
    company = models.CharField(
        max_length=64,
        blank=True,
        help_text="The company this person if affiliated with.",
    )
    birthday = models.DateField(
        blank=True,
        null=True,
        help_text="If this is not required, just leave this blank.",
    )

    username = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        null=True,
        blank=True,
        help_text="Username on the local system, if the person has one. 64 characters or fewer. Letters, numbers and "
        "@/./+/-/_ characters",
        validators=[
            validators.RegexValidator(
                re.compile(r"^[\w.@+-]+$"), "Enter a valid username.", "invalid"
            )
        ],
    )
    slug = AutoSlugField(
        unique=True,
        db_index=True,
        null=True,
        blank=True,
        populate_from=conf.get("person:slug:populate_from"),
        verbose_name="URL fragment",
    )

    note = models.TextField(blank=True)

    objects = PersonManager()

    class Meta:
        ordering = ["sn", "given_name"]
        verbose_name_plural = "people"
        base_manager_name = "objects"

    def __str__(self):
        return self.cn

    def clean(self, *args, **kwargs):
        """
        This bit of magic is to allow unique but empty for undefined or unrequired UserIDs.
        Source: http://www.hoboes.com/Mimsy/hacks/django-empty-strings/ [2009-Oct-20]
        """
        if self.username == "":
            self.username = None
        if self.slug == "":
            self.slug = None
        if self.cn == "":
            self.cn = self.given_name + " " + self.sn
        super(Person, self).clean(*args, **kwargs)

    if PERSON_PERMALINK is not None:

        def get_absolute_url(self):
            """
            This bit of magic is to allow a completely plugable system for
            personal pages.
            Note that personal pages are not guaranteed to exist when a person
            exists; even when they have a slug.
            """
            if isinstance(PERSON_PERMALINK, (tuple, list)):
                view_name, arg_callable_string = PERSON_PERMALINK
                if callable(arg_callable_string):
                    arg_callable = arg_callable_string
                else:
                    mod_name, f_name = arg_callable_string.rsplit(".", 1)
                    arg_callable = getattr(import_module(mod_name), f_name)
                args = arg_callable(self)
                if args is not None:
                    return reverse(view_name, args=args)
            elif callable(PERSON_PERMALINK):
                return PERSON_PERMALINK(self)
            elif isinstance(PERSON_PERMALINK, str):
                mod_name, f_name = arg_callable_string.rsplit(".", 1)
                f = getattr(import_module(mod_name), f_name)
                return f(self)
            return None

    ##################
    ## The following methods deal with changing a person's flags
    ##################

    def add_flag_by_name(self, slug, verbose_name=None):
        """
        Add the named PersonFlag to this person.  Create if necessary.

        Verbose name and verbose name plural, if given, are defaults only.
        """
        if not verbose_name:
            verbose_name = slug

        obj, created = PersonFlag.objects.get_or_create(
            slug=slug, defaults={"verbose_name": verbose_name}
        )

        if obj not in self.flags.all():
            self.flags.add(obj)

    def remove_flag_by_name(self, slug):
        """
        Remove the named PersonFlag from this person.
        """
        try:
            obj = PersonFlag.objects.get(slug=slug)
        except PersonFlag.DoesNotExist:
            return  # not a valid flag slug
        self.flags.remove(obj)

    def has_flag(self, slug):
        """
        Returns true if the user has the flag, False otherwise.
        """
        return self.flags.filter(slug=slug).count() > 0

    ######################
    def get_user(self):
        """
        Retrieve the corresponding user object, if it exists
        """
        return get_user_model().objects.get(username=self.username)

    ######################
    ## The following utility methods deal with setting and retrieving
    ## contact information.
    ######################

    def add_contact_info(self, type_, ci_type_slug, **data):
        ci_type, ci_flag = ContactInfoType.objects.get_or_create(
            slug=ci_type_slug,
            defaults={
                "verbose_name": ci_type_slug.title(),
                "verbose_name_plural": ci_type_slug.title(),
            },
        )
        preferred = data.pop("preferred", False)
        public = data.pop("public", False)
        verified = data.pop("verified", False)
        # data['type'] = ci_type

        data["person"] = self
        # if it already exists; but has a different type (or preferred,
        # public, or verified); that's fine. (particularly: email)
        obj, flag = type_.objects.get_or_create(
            **data,
            defaults={
                "type": ci_type,
                "preferred": preferred,
                "public": public,
                "verified": verified,
            }
        )
        if preferred:  # clear any other preferreds on this type_, for this person
            type_.objects.filter(person=self, type=ci_type).exclude(pk=obj.pk).update(
                preferred=False
            )
            if not obj.preferred:
                obj.preferred = True
                obj.save()
        return obj

    def add_email(self, address, type_slug, preferred=False, **kwargs):
        kwargs["preferred"] = preferred
        return self.add_contact_info(EmailAddress, type_slug, address=address, **kwargs)

    def add_phone(self, number, type_slug, preferred=False):
        return self.add_contact_info(
            PhoneNumber, type_slug, number=number, preferred=preferred
        )

    def add_address(self, data, type_slug, preferred=False):
        return self.add_contact_info(
            StreetAddress, type_slug, preferred=preferred, **data
        )

    def get_contact_info(self, type_, ci_type_slug=None):
        """
        This method *only* returns items that are public.
        """
        qs = type_.objects.filter(active=True, person=self, public=True)
        if ci_type_slug is not None:
            qs = qs.filter(type__slug=ci_type_slug)

        info = list(qs)  # force evalutation: 1 query.
        if not info:
            return None
        if any([i.preferred for i in info]):
            for i in info:
                if i.preferred:
                    return i
        return info[0]

    def get_phone_number(self, ci_type_slug=None):
        return self.get_contact_info(PhoneNumber, ci_type_slug)

    def get_email_address(self, ci_type_slug=None):
        return self.get_contact_info(EmailAddress, ci_type_slug)

    def get_street_address(self, ci_type_slug=None):
        return self.get_contact_info(StreetAddress, ci_type_slug)

    @property
    def phone(self):
        return self.get_phone_number()

    @property
    def email(self):
        return self.get_email_address()

    @property
    def address(self):
        return self.get_street_address()

    @property
    def extra_data(self):
        return {
            k.replace("-", "_"): v
            for k, v in self.personkeyvalue_set.active()
            .filter(key__active=True)
            .values_list("key__slug", "value")
        }

    ######################


if conf.get("autoslug"):
    models.signals.pre_save.connect(handlers.person_pre_save_set_slug, sender=Person)

###############################################################


@python_2_unicode_compatible
class ContactInfoType(models.Model):
    """
    ContactInfoType

    Types of contact information.
    Examples include: home, work, mobile, fax.
    """

    active = models.BooleanField(default=True)
    slug = AutoSlugField(max_length=32, populate_from="verbose_name_plural")
    verbose_name = models.CharField(max_length=32)
    verbose_name_plural = models.CharField(max_length=32)

    class Meta:
        ordering = ["verbose_name"]

    def __str__(self):
        return self.verbose_name


###############################################################


class BaseContactInfo(PeopleBaseModel):
    """
    Abstract base class for contact information.
    """

    public = models.BooleanField(default=False)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    type = models.ForeignKey(ContactInfoType, on_delete=models.PROTECT)
    preferred = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = ["-preferred"]


###############################################################


@python_2_unicode_compatible
class PhoneNumber(BaseContactInfo):
    """
    A phone number
    """

    number = PhoneNumberField()

    objects = BaseContactInfoManager()

    class Meta:
        unique_together = ["person", "number"]
        base_manager_name = "objects"

    def __str__(self):
        return str(self.number)


###############################################################


@python_2_unicode_compatible
class EmailAddress(BaseContactInfo):
    """
    An email address
    """

    address = models.EmailField(max_length=128)

    objects = BaseContactInfoManager()

    class Meta:
        unique_together = (("person", "address"),)
        # NOTE:
        # Despite the thinking that "everybody has their own email address",
        # the reality is that people *share* email addresses, including
        # incoming students from high school that haven't yet claimed
        # their UMnetID.  One person should not have duplicates of the same
        # address however.
        verbose_name_plural = "email addresses"
        ordering = ["-public", "-preferred", "-verified", "address"]
        # ordering reflects email address "priority"
        # remember that True sorts AFTER False (1 comes after 0).
        # public address first, then preferred ones, then verified ones
        base_manager_name = "objects"

    def __str__(self):
        return str(self.address)


###############################################################


@python_2_unicode_compatible
class StreetAddress(BaseContactInfo):
    """
    Address

    An address.
    """

    street_1 = models.CharField(max_length=128, blank=True)
    street_2 = models.CharField(max_length=128, blank=True, help_text="Optional")
    city = models.CharField(
        max_length=64, blank=True, help_text="(Township, Municipality, etc.)"
    )
    region = RegionField(blank=True, help_text="Provinces in Canada, States for U.S.A.")
    country = models.CharField(max_length=64, blank=True)
    postal_code = PostalCodeField(blank=True)

    objects = BaseContactInfoManager()

    class Meta:
        verbose_name_plural = "street addresses"
        base_manager_name = "objects"

    def __str__(self):
        return "{}".format(self.type).upper() + ": " + "; ".join(self.as_lines())

    def as_lines(self):
        result = []
        if self.street_1:
            result.append(self.street_1)
        if self.street_2:
            result.append(self.street_2)
        if self.city:
            result.append(self.city)
        if self.region:
            result.append(self.region)
        if self.country:
            result.append(self.country)
        if self.postal_code:
            result.append(self.postal_code)
        return result


###############################################################


@python_2_unicode_compatible
class EmailConfirmation(PeopleBaseModel):
    """
    Inspired by django-registration
    """

    VERIFIED = "ALREADY_VERIFIED"

    email = models.OneToOneField(EmailAddress, on_delete=models.CASCADE)
    key = models.CharField(max_length=64)
    email_send_time = models.DateTimeField(
        null=True,
        help_text="If this is not set, the verification email has "
        + "<em>not</em> been sent.",
    )
    redirect_url = models.URLField(blank=True)
    delete_unverified = models.BooleanField(
        default=False,
        help_text="If this is set, unverified email addresses and "
        + "people objects will be deleted",
    )

    objects = EmailConfirmationManager()

    def __str__(self):
        return "{}".format(self.email) + ": " + self.key

    def set_verified(self, set_email=True):
        self.key = self.VERIFIED
        self.save()
        if set_email:
            self.email.verified = True
            self.email.save()

    def is_verified(self):
        return self.key == self.VERIFIED

    def is_valid(self):
        """
        EmailConfirmation objects are only valid when:
        * they are not yet verified,
        * they confirmation email has been sent
        * the confirmation email was sent recently enough.
        """
        if self.is_verified():
            return False  # already verified
        timeout_hours = conf.get("verification_timeout")
        if self.email_send_time is None:
            return False  # no email sent: this is expired
        now = datetime.datetime.now()
        expiration_dt = now + datetime.timedelta(hours=timeout_hours)
        return expiration_dt <= now

    def send_email(
        self,
        site,
        subject_template=DEFAULT_CONFIRM_SUBJECT_TEMPLATE,
        body_template=DEFAULT_CONFIRM_BODY_TEMPLATE,
        extra_email_context=None,
    ):
        """
        Note that the templates can be lists, as in render();
        extra_email_context, if given, should be a dictionary like object.
        """

        timeout_hours = conf.get("verification_timeout")
        now = datetime.datetime.now()
        expiration_dt = now + datetime.timedelta(hours=timeout_hours)
        self.email_send_time = now

        if extra_email_context is None:
            extra_email_context = {}

        if site is None:
            site = Site.objects.get_current()

        context = {"site": site, "expiration_dt": expiration_dt, "verify": self}
        context.update(extra_email_context)

        subject = render_to_string(subject_template, context)
        # the subject must not contain multiple lines
        subject = " ".join(subject.splitlines())
        # also, trim whitespace:
        subject = subject.replace("\t", " ")
        while "  " in subject:
            subject = subject.replace("  ", " ")

        body = render_to_string(body_template, context)

        email = EmailMessage(subject=subject, body=body, to=[self.email.address])
        email.send()
        self.save()  # save AFTER the email goes out.
        return True  # email sent!


###############################################################


@python_2_unicode_compatible
class PersonKey(PeopleBaseModel):
    slug = AutoSlugField(max_length=64, populate_from="verbose_name", unique=True)
    verbose_name = models.CharField(max_length=64)

    objects = PersonKeyQuerySet.as_manager()

    class Meta:
        verbose_name = "additional person field"
        ordering = ["verbose_name"]
        base_manager_name = "objects"

    def __str__(self):
        return self.verbose_name


###############################################################


@python_2_unicode_compatible
class PersonKeyValue(PeopleBaseModel):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    key = models.ForeignKey(PersonKey, verbose_name="Field", on_delete=models.CASCADE)
    value = models.CharField(max_length=256)

    objects = PersonKeyValueQuerySet.as_manager()

    class Meta:
        verbose_name = "additional data"
        verbose_name_plural = "additional data"
        base_manager_name = "objects"
        unique_together = [["person", "key"]]

    def __str__(self):
        return self.value


###############################################################
