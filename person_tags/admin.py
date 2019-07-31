"""
Admin hooks for person_tags.
"""
from django.contrib import admin

from .forms import TagGroupAdminForm
from .models import Asset, PersonTag, PersonTaggedEntry, TagGroup

##############################################################


def mark_inactive(modeladmin, request, queryset):
    queryset.update(active=False)


mark_inactive.short_description = "Mark selected items as inactive"

######################################################


class PersonTagAdmin(admin.ModelAdmin):
    list_display = ["tag", "active"]
    search_fields = ["slug", "tag"]
    list_filter = ["active", "created", "modified"]
    prepopulated_fields = {"slug": ("tag",)}
    fieldsets = ((None, {"fields": ["active", "tag", "slug"]}),)
    actions = [mark_inactive]


admin.site.register(PersonTag, PersonTagAdmin)

######################################################


class PersonTaggedEntryAdmin(admin.ModelAdmin):
    autocomplete_fields = ["person", "tag"]
    list_display = ["person", "tag", "active", "ordering"]
    search_fields = ["person__cn", "tag__tag"]
    list_filter = ["active", "person", "tag", "created", "modified"]
    actions = [mark_inactive]


admin.site.register(PersonTaggedEntry, PersonTaggedEntryAdmin)

######################################################


class AssetInline(admin.TabularInline):
    model = Asset
    fields = ["file", "description", "get_absolute_url"]
    readonly_fields = ["get_absolute_url"]
    extra = 0


###############################################################


class TagGroupAdmin(admin.ModelAdmin):
    actions = [mark_inactive]
    autocomplete_fields = ["tags"]
    filter_horizontal = ("tags",)
    form = TagGroupAdminForm
    inlines = [AssetInline]
    list_display = ["name", "slug", "active"]
    list_filter = ["active", "created", "modified"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["slug", "name", "description"]


admin.site.register(TagGroup, TagGroupAdmin)

######################################################
