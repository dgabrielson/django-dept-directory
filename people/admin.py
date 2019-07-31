"""
Admin hooks for people.
"""
from functools import update_wrapper

from directory.mixins import DefaultFilterMixin, LabelAutocompleteJsonView
from django.contrib import admin
from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.contrib.admin.widgets import AutocompleteSelect
from django.urls import reverse

from . import conf
from .forms import AdminEmailAddressForm, AdminPhoneNumberForm, AdminStreetAddressForm
from .models import (
    ContactInfoType,
    EmailAddress,
    Person,
    PersonFlag,
    PersonKey,
    PersonKeyValue,
    PhoneNumber,
    StreetAddress,
)

######################################################


class FlagFilterAutocompleteJsonView(LabelAutocompleteJsonView):
    """
    A view which only returns filtered person results.
    """

    flag = None

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(flags__slug=self.flag)
        return qs


class FlagFilterAutocompleteSelect(AutocompleteSelect):
    """
    This widget can be used in other admins that require a filtered
    list of people, but still want autocomplete.
    To use:
from people.admin import FlagFilterAutocompleteSelect
#...
class MyModelAdmin(admin.ModelAdmin):
    ...
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "instructor":
            db = kwargs.get("using")
            # The ``flag`` kwarg specifies which person flag (slug)
            #   to filter on.
            kwargs["widget"] = FlagFilterAutocompleteSelect(
                db_field.remote_field, self.admin_site, using=db,
                flag='instructor')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    """

    def __init__(self, *args, **kwargs):
        self._flag = kwargs.pop("flag")
        if self._flag is None:
            raise RuntimeError(
                "you must supply a flag= argument to FlagFilterAutocompleteSelect instances"
            )
        return super().__init__(*args, **kwargs)

    def get_url(self):
        return reverse(
            "admin:people_person_flagfilter_autocomplete", kwargs={"flag": self._flag}
        )


######################################################


class ContactInfoTypeAdmin(admin.ModelAdmin):
    list_display = ["verbose_name", "active"]
    search_fields = ["slug", "verbose_name", "verbose_name_plural"]
    list_filter = ["active"]
    prepopulated_fields = {"verbose_name_plural": ("verbose_name",)}
    fieldsets = (
        (None, {"fields": ["active", "verbose_name", "verbose_name_plural", "slug"]}),
    )
    readonly_fields = ["slug"]


admin.site.register(ContactInfoType, ContactInfoTypeAdmin)

######################################################


class PersonFlagAdmin(admin.ModelAdmin):
    list_display = ["verbose_name", "slug", "active"]
    search_fields = ["slug", "verbose_name"]
    list_filter = ["active"]
    fieldsets = ((None, {"fields": ["active", "verbose_name", "slug"]}),)
    readonly_fields = ["slug"]


admin.site.register(PersonFlag, PersonFlagAdmin)

######################################################


class PersonKeyAdmin(admin.ModelAdmin):
    list_display = ["verbose_name", "slug", "active"]
    search_fields = ["slug", "verbose_name"]
    list_filter = ["active"]
    readonly_fields = ["slug"]


admin.site.register(PersonKey, PersonKeyAdmin)

######################################################


class PhoneNumberInline(admin.TabularInline):
    form = AdminPhoneNumberForm
    model = PhoneNumber
    extra = 0


class EmailAddressInline(admin.TabularInline):
    form = AdminEmailAddressForm
    model = EmailAddress
    extra = 0
    readonly_fields = ["verified"]


class StreetAddressInline(admin.StackedInline):
    form = AdminStreetAddressForm
    model = StreetAddress
    extra = 0
    classes = ["collapse", "collapsed"]


class PersonKeyValueInline(admin.TabularInline):
    model = PersonKeyValue
    extra = 0


class PersonAdmin(DefaultFilterMixin, admin.ModelAdmin):
    autocomplete_fields = ["flags"]
    inlines = [
        PhoneNumberInline,
        EmailAddressInline,
        StreetAddressInline,
        PersonKeyValueInline,
    ]
    filter_horizontal = ("flags",)
    list_display = ["cn", "title", "company", "username", "active"]
    search_fields = ["cn", "sn", "given_name", "title", "company", "username", "slug"]
    list_filter = ["active", "flags"]
    save_on_top = True
    fieldsets = (
        (
            None,
            {
                "fields": [
                    "active",
                    ("sn", "given_name"),
                    ("cn", "sync_name"),
                    "title",
                    "flags",
                    "username",
                    "slug",
                ]
            },
        ),
        (
            "Optional Information",
            {"classes": ["collapse"], "fields": ["company", "birthday", "note"]},
        ),
    )
    readonly_fields = ["slug"]

    def view_on_site(self, obj):
        return obj.get_absolute_url()

    def get_default_filters(self, request):
        """Set default filters to the page.
            request (Request)
            Returns (dict):
                Default filter to encode.
        """
        return conf.get("admin_person_default_query")

    def autocomplete_view(self, request):
        return LabelAutocompleteJsonView.as_view(
            autocomplete_text=self.autocomplete_text, model_admin=self
        )(request)

    def autocomplete_text(self, obj):
        "change this to update the text of autocomplete for this object"
        if obj.username:
            return "{} [{}]".format(obj, obj.username)
        if obj.emailaddress_set.exists():
            email_addr = obj.emailaddress_set.all()[0]
            return "{} [{}]".format(obj, email_addr)
        return str(obj)

    def flagfilter_autocomplete_view(self, request, **kwargs):
        return FlagFilterAutocompleteJsonView.as_view(
            autocomplete_text=self.autocomplete_text, model_admin=self, **kwargs
        )(request)

    def get_urls(self):
        from django.urls import path

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        return [
            path(
                "autocomplete-filter/<flag>/",
                wrap(self.flagfilter_autocomplete_view),
                name="people_person_flagfilter_autocomplete",
            )
        ] + super().get_urls()


admin.site.register(Person, PersonAdmin)

######################################################
