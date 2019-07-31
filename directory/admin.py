# -*- coding: utf-8 -*-
"""
Admin hooks for directory.
"""
from django.conf.urls import url
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from people.admin import FlagFilterAutocompleteSelect

from .models import DirectoryEntry, EntryType
from .views import PrintDirectory

##############################################################


def mark_inactive(modeladmin, request, queryset):
    queryset.update(active=False)


mark_inactive.short_description = "Mark selected items as inactive"

##############################################################


class DirectoryEntryInline(admin.TabularInline):
    model = DirectoryEntry
    fields = ["active", "person", "office", "title"]
    extra = 0


##############################################################


class EntryTypeAdmin(admin.ModelAdmin):
    actions = [mark_inactive, "print_directory"]
    inlines = [DirectoryEntryInline]
    list_display = ["verbose_name", "active"]
    search_fields = ["slug", "verbose_name", "verbose_name_plural"]
    list_filter = ["active"]
    prepopulated_fields = {"slug": ("verbose_name",)}
    fieldsets = (
        (
            None,
            {
                "fields": [
                    "active",
                    "verbose_name",
                    "verbose_name_plural",
                    "slug",
                    "ordering",
                ]
            },
        ),
    )
    save_on_top = True

    def get_urls(self, *args, **kwargs):
        """
        Extend the admin urls for this model.
        Provide a link by subclassing the admin change_form,
        and adding to the object-tools block.
        """
        urls = super(EntryTypeAdmin, self).get_urls(*args, **kwargs)
        urls = [
            url(
                r"^print-directory/$",
                self.admin_site.admin_view(PrintDirectory.as_view()),
                name="directory-entrytype-print",
            )
        ] + urls
        return urls

    def print_directory(self, request, queryset):
        """
        Redirect to the actual view.
        """
        url = reverse_lazy("admin:directory-entrytype-print")
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        query = "&".join(["pk={0}".format(s) for s in selected])
        return HttpResponseRedirect(url + "?" + query)

    print_directory.short_description = (
        "Generate PDF directory for selected entry types"
    )


admin.site.register(EntryType, EntryTypeAdmin)

######################################################


class DirectoryEntryAdmin(admin.ModelAdmin):
    autocomplete_fields = ["person", "type", "office"]
    list_display = ["person", "type", "office", "active"]
    search_fields = ["person__cn", "title"]
    list_filter = ["active", "person__active", "type"]

    actions = [mark_inactive]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "person":
            db = kwargs.get("using")
            # The ``flag`` kwarg specifies which person flag (slug)
            #   to filter on.
            kwargs["widget"] = FlagFilterAutocompleteSelect(
                db_field.remote_field, self.admin_site, using=db, flag="directory"
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def view_on_site(self, obj):
        return obj.get_absolute_url()


admin.site.register(DirectoryEntry, DirectoryEntryAdmin)

######################################################
