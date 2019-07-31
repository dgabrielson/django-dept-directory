"""
Forms for the directory application.
"""
###############################################################

from collections import OrderedDict

from django import forms
from django.conf import settings
from django.forms.utils import ErrorDict

from .models import DirectoryEntry

###############################################################


class DirectoryEntryForm(forms.ModelForm):
    """
    A form for updating directory entries.
    """

    class Meta:
        model = DirectoryEntry
        exclude = ["active", "person", "type", "title", "office", "ordering"]
        widgets = {
            "url": forms.TextInput(attrs={"size": 80}),
            "note": forms.TextInput(attrs={"size": 80}),
        }

    class Media:
        css = {
            "all": (
                settings.STATIC_URL + "css/forms.css",
                settings.STATIC_URL + "css/twoColumn.css",
            )
        }


###############################################################


class DirectoryEntryPersonSubForm(forms.ModelForm):
    """
    The sub form for the person form.
    """

    subform_title = "Directory entry"

    class Meta:
        model = DirectoryEntry
        fields = ["active", "type", "title", "office", "url", "note"]
        widgets = {
            "url": forms.TextInput(attrs={"size": 50}),
            "note": forms.TextInput(attrs={"size": 50}),
        }

    def __init__(self, data=None, *args, **kwargs):
        """
        If instance is passed, then we must resolve this: it is a person!
        """
        if "instance" in kwargs and kwargs["instance"] is not None:
            person = kwargs["instance"]
            object_list = person.directoryentry_set.all()
            if object_list.count() > 0:
                kwargs["instance"] = object_list[0]
            else:
                del kwargs["instance"]  # no instance

        result = super(DirectoryEntryPersonSubForm, self).__init__(
            data, *args, **kwargs
        )
        # allow for this sub-object to *not* be created:
        if "instance" not in kwargs or kwargs["instance"] is None:
            f = forms.BooleanField(label="Create directory entry", required=False)
            self.fields = OrderedDict([("_do_create", f)] + list(self.fields.items()))
            self.initial["_do_create"] = True
            del self.fields["active"]  # of course it will be active, if created.
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
            return super(DirectoryEntryPersonSubForm, self).full_clean(*args, **kwargs)

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
        obj = super(DirectoryEntryPersonSubForm, self).save(*args, **kwargs)
        obj.person = person

        if original_commit is not None:
            kwargs["commit"] = original_commit
        else:
            del kwargs["commit"]
        # check original commit:
        if original_commit != False:  # None \equiv True
            person.add_flag_by_name("directory")

        return super(DirectoryEntryPersonSubForm, self).save(*args, **kwargs)


###############################################################
