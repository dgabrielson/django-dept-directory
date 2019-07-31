"""
Forms for the people app.
"""
###############################################################

from collections import OrderedDict
from importlib import import_module

from django import forms
from django.forms.models import construct_instance
from django.forms.utils import ErrorDict

from . import conf
from .models import ContactInfoType, EmailAddress, Person, PhoneNumber, StreetAddress

###############################################################


class AdminEmailAddressForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = EmailAddress


###############################################################


class AdminPhoneNumberForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = PhoneNumber


###############################################################


class AdminStreetAddressForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = StreetAddress


###############################################################


class AdminPersonForm(forms.ModelForm):
    """
    A form for creating and updating people, and related items.
    This form acts as a container for all defined extra_person_forms.
    """

    subform_title = "Personal information"

    class Meta:
        model = Person
        fields = conf.get("admin_person_fields")

    class Media:
        css = {"all": ("css/forms.css", "css/twoColumn.css")}

    def __init__(self, *args, **kwargs):
        kwargs["prefix"] = "form.0"  # special prefix handling for multi-form.
        result = super(AdminPersonForm, self).__init__(*args, **kwargs)
        if "instance" in kwargs and kwargs["instance"] is not None:
            if "slug" in self.fields and kwargs["instance"].slug:
                # It is a very, very bad idea to change the slug
                # for a person record.
                del self.fields["slug"]
            if "username" in self.fields and kwargs["instance"].username:
                # usernames do not change
                del self.fields["username"]

        self._load_extra_forms(*args, **kwargs)
        return result

    def _load_extra_forms(self, *args, **kwargs):
        """
        Load the extra forms.
        NOTE: the args and kwargs are passed to every extra form constructor.

        Every form requires a prefix, since everything is in one <form> tag.
        """
        extra_forms = []
        # original_prefix = kwargs.get('prefix', None)
        counter = 1
        for form_name in conf.get("extra_person_forms"):
            # assume this is module.FormClass format.
            module_name, class_name = form_name.rsplit(".", 1)
            module = import_module(module_name)
            form_class = getattr(module, class_name)
            kwargs["prefix"] = "form.{0}".format(counter)
            form_instance = form_class(*args, **kwargs)
            extra_forms.append(form_instance)
            counter += 1

        self.extra_forms = extra_forms

    def full_clean(self, *args, **kwargs):
        """
        **Clean** all the things
        """
        result = super(AdminPersonForm, self).full_clean(*args, **kwargs)
        for form in self.extra_forms:
            form.full_clean(*args, **kwargs)  # should raise ValidationError
        return result

    def is_valid(self, *args, **kwargs):
        """
        If anything is not valid, the whole is not valid.
        """
        base = super(AdminPersonForm, self).is_valid(*args, **kwargs)
        others = [f.is_valid(*args, **kwargs) for f in self.extra_forms]
        return base and all(others)

    def save(self, *args, **kwargs):
        """
        **Save** all the things
        """
        person = super(AdminPersonForm, self).save(*args, **kwargs)
        for form in self.extra_forms:
            form.save(person, *args, **kwargs)
        return person


###############################################################


class PersonFlagsPersonSubForm(forms.ModelForm):
    """
    For dealing with personFlags.
    """

    subform_title = "Flags"

    class Meta:
        model = Person
        fields = ["flags"]  # person fk *must not* be editable.
        widgets = {"flags": forms.CheckboxSelectMultiple}
        help_texts = {"flags": ""}  # Django 1.6+

    # help texts shim for Django <1.6
    def __init__(self, *args, **kwargs):
        result = super(PersonFlagsPersonSubForm, self).__init__(*args, **kwargs)
        for key in self.Meta.help_texts:
            self.fields[key].help_text = self.Meta.help_texts[key]
        return result

    def save(self, person, commit=True):
        """
        Saves this ``form``'s cleaned_data into model instance
        ``self.instance``.

        If commit=True, then the changes to ``instance`` will be saved to the
        database. Returns ``instance``.
        """
        self.instance = person
        return super(PersonFlagsPersonSubForm, self).save(commit=commit)

    save.alters_data = True


###############################################################


class EmailAddressPersonSubForm(forms.ModelForm):
    """
    This is an extra for AdminPersonForm and follows the required API
    (See person_subforms_api.txt.)
    """

    subform_title = "Email address"

    class Meta:
        model = EmailAddress
        fields = ["address", "public"]  # person fk *must not* be editable.
        widgets = {"address": forms.TextInput(attrs={"size": 50})}

    def __init__(self, data=None, *args, **kwargs):
        """
        If instance is passed, then we must resolve this: it is a person!
        """
        if "instance" in kwargs and kwargs["instance"] is not None:
            person = kwargs["instance"]
            emailaddress_list = person.emailaddress_set.active()
            if emailaddress_list.count() > 0:
                kwargs["instance"] = emailaddress_list[0]
            else:
                del kwargs["instance"]  # no instance
        result = super(EmailAddressPersonSubForm, self).__init__(data, *args, **kwargs)
        # allow for this sub-object to *not* be created:
        if "instance" not in kwargs or kwargs["instance"] is None:
            f = forms.BooleanField(label="Create email address", required=False)
            self.fields = OrderedDict([("_do_create", f)] + list(self.fields.items()))
            self.initial["_do_create"] = True
            self.initial["public"] = True  # will be true for employees, etc.
            # when NOT creating (if we could have)... nothing is required:
            if data and not data.get(self.get_do_create_field_name(), False):
                for key in self.fields:
                    self.fields[key].required = False

        return result

    def get_do_create_field_name(self):
        if self.prefix:
            prefix_field = self.prefix + "-" + "_do_create"
        else:
            prefix_field = "_do_create"
        return prefix_field

    def full_clean(self, *args, **kwargs):
        """
        Override clean behaviour when _do_create is *not* set.
        """
        self._errors = ErrorDict()
        if not self.is_bound:  # Stop further processing.
            return
        if "_do_create" in self.fields and not self.data.get(
            self.get_do_create_field_name(), False
        ):
            self.cleaned_data = {"_do_create": False}
        else:
            return super(EmailAddressPersonSubForm, self).full_clean(*args, **kwargs)

    def save(self, person, *args, **kwargs):
        """
        Each save() must reinsert the person, along with any other required
        fields that are not shown.
        """
        # allow for this sub-object to *not* be created:
        if "_do_create" in self.fields and self.cleaned_data["_do_create"] == False:
            return None
        original_commit = kwargs.get("commit", None)
        kwargs["commit"] = False
        obj = super(EmailAddressPersonSubForm, self).save(*args, **kwargs)
        obj.person = person
        if obj.type_id is None:
            # WARNING: accessing obj.type causes bad things to happen.
            ci_type_slug = conf.get("default_contact_info_type")
            ci_type, ci_flag = ContactInfoType.objects.get_or_create(
                slug=ci_type_slug,
                defaults={
                    "verbose_name": ci_type_slug.title(),
                    "verbose_name_plural": ci_type_slug.title(),
                },
            )
            obj.type = ci_type

        if original_commit is not None:
            kwargs["commit"] = original_commit
        else:
            del kwargs["commit"]

        return super(EmailAddressPersonSubForm, self).save(*args, **kwargs)


###############################################################


class PhonePersonSubForm(forms.ModelForm):
    """
    This is an extra for AdminPersonForm and follows the required API
    (See person_subforms_api.txt.)
    """

    subform_title = "Phone number"

    class Meta:
        model = PhoneNumber
        fields = ["number", "public"]  # person fk *must not* be editable.
        widgets = {"number": forms.TextInput(attrs={"size": 50})}

    def get_actual_instance(self, person):
        """
        Transform the person into the actual instance for this form.
        Return None if it cannot be done.
        """
        phonenumber_list = person.phonenumber_set.active()
        if phonenumber_list.count() > 0:
            return phonenumber_list[0]
        return None

    def __init__(self, data=None, *args, **kwargs):
        """
        If instance is passed, then we must resolve this: it is a person!
        """
        if "instance" in kwargs and kwargs["instance"] is not None:
            actual_instance = self.get_actual_instance(kwargs["instance"])
            if actual_instance is not None:
                kwargs["instance"] = actual_instance
            else:
                del kwargs["instance"]  # no instance
        result = super(PhonePersonSubForm, self).__init__(data, *args, **kwargs)
        # allow for this sub-object to *not* be created:
        if "instance" not in kwargs or kwargs["instance"] is None:
            f = forms.BooleanField(
                label="Create " + self.subform_title.lower(), required=False
            )
            self.fields = OrderedDict([("_do_create", f)] + self.fields.items())
            self.initial["_do_create"] = True
            self.initial["public"] = True  # will be true for employees, etc.
            # when NOT creating (if we could have)... nothing is required:
            if data and not data.get(self.get_do_create_field_name(), False):
                for key in self.fields:
                    self.fields[key].required = False

        return result

    def get_do_create_field_name(self):
        if self.prefix:
            prefix_field = self.prefix + "-" + "_do_create"
        else:
            prefix_field = "_do_create"
        return prefix_field

    def full_clean(self, *args, **kwargs):
        """
        Override clean behaviour when _do_create is *not* set.
        """
        self._errors = ErrorDict()
        if not self.is_bound:  # Stop further processing.
            return
        if "_do_create" in self.fields and not self.data.get(
            self.get_do_create_field_name(), False
        ):
            self.cleaned_data = {"_do_create": False}
        else:
            return super(PhonePersonSubForm, self).full_clean(*args, **kwargs)

    def save(self, person, *args, **kwargs):
        """
        Each save() must reinsert the person, along with any other required
        fields that are not shown.
        """
        # allow for this sub-object to *not* be created:
        if "_do_create" in self.fields and self.cleaned_data["_do_create"] == False:
            return None
        original_commit = kwargs.get("commit", None)
        kwargs["commit"] = False
        obj = super(PhonePersonSubForm, self).save(*args, **kwargs)
        obj.person = person
        if obj.type_id is None:
            # WARNING: accessing obj.type causes bad things to happen.
            ci_type_slug = conf.get("default_contact_info_type")
            ci_type, ci_flag = ContactInfoType.objects.get_or_create(
                slug=ci_type_slug,
                defaults={
                    "verbose_name": ci_type_slug.title(),
                    "verbose_name_plural": ci_type_slug.title(),
                },
            )
            obj.type = ci_type

        if original_commit is not None:
            kwargs["commit"] = original_commit
        else:
            del kwargs["commit"]

        return super(PhonePersonSubForm, self).save(*args, **kwargs)


###############################################################
