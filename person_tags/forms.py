from django import forms
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.forms.models import inlineformset_factory
from django.template.defaultfilters import slugify, truncatechars
from markuphelpers.forms import LinedTextareaWidget, ReStructuredTextFormMixin
from people.models import Person

from .models import PersonTag, PersonTaggedEntry, TagGroup

## ######################################################### ##


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = []  # an emtpy form!

    class Media:
        css = {
            "all": (
                staticfiles_storage.url("css/forms.css"),
                staticfiles_storage.url("css/twoColumn.css"),
            )
        }
        js = (staticfiles_storage.url("js/jquery.formset.js"),)


## ######################################################### ##


class TagModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return truncatechars(obj.tag, 100)


class PersonTaggedEntryFormSet(forms.ModelForm):
    tag = TagModelChoiceField(queryset=PersonTag.objects.active())

    class Meta:
        model = PersonTaggedEntry
        fields = ["active", "tag", "ordering"]
        widgets = {"ordering": forms.TextInput(attrs={"size": 8})}


#######################################################################


def get_persontaggedentry_formset_class(
    form=PersonTaggedEntryFormSet, formset=forms.BaseInlineFormSet, **kwargs
):
    return forms.inlineformset_factory(
        Person, PersonTaggedEntry, form, formset, **kwargs
    )


## ######################################################### ##


class PersonTagForm(forms.ModelForm):
    class Meta:
        model = PersonTag
        exclude = ["active", "slug"]
        widgets = {"tag": forms.TextInput(attrs={"size": 60})}

    class Media:
        css = {
            "all": (
                staticfiles_storage.url("css/forms.css"),
                staticfiles_storage.url("css/twoColumn.css"),
            )
        }

    def clean_tag(self):
        self.slug = slugify(self.data["tag"])
        if PersonTag.objects.filter(slug=self.slug).count() != 0:
            raise forms.ValidationError("This tag already exists.")
        return self.data["tag"]

    def save(self, *args, **kwargs):
        self.instance.slug = self.slug
        return super(PersonTagForm, self).save(*args, **kwargs)


## ######################################################### ##


class TagGroupAdminForm(ReStructuredTextFormMixin, forms.ModelForm):
    """
    The form for tag groups in the Django admin.
    """

    restructuredtext_fields = [("description", True)]

    class Meta:
        model = TagGroup
        widgets = {"description": LinedTextareaWidget}
        exclude = []


## ######################################################### ##
