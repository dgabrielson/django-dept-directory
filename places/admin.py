# -*- coding: utf-8 -*-
"""
Admin hooks for places.
"""
from django.contrib import admin
from places.models import *

######################################################


class ClassRoom_Options(admin.ModelAdmin):
    list_display = ["slug", "number", "building", "capacity", "note", "active"]
    list_editable = ["capacity", "note"]
    search_fields = ["slug", "number", "building", "note"]
    list_filter = ["active", "building"]
    prepopulated_fields = {"slug": ("number", "building")}
    fieldsets = (
        (
            None,
            {"fields": ["active", "number", "building", "slug", "capacity", "note"]},
        ),
    )


admin.site.register(ClassRoom, ClassRoom_Options)

######################################################


class Office_Options(admin.ModelAdmin):
    list_display = ["slug", "number", "building", "phone_number", "note", "active"]
    list_editable = ["phone_number", "note"]
    search_fields = ["slug", "number", "building", "phone_number"]
    list_filter = ["active", "building"]
    prepopulated_fields = {"slug": ("number", "building")}
    fieldsets = (
        (
            None,
            {
                "fields": [
                    "active",
                    "number",
                    "building",
                    "slug",
                    "phone_number",
                    "note",
                ]
            },
        ),
    )


admin.site.register(Office, Office_Options)

######################################################
