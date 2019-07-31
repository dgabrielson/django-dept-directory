# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-19 20:04
from __future__ import unicode_literals

import autoslug.fields
import directory
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("people", "0011_auto_20170919_1458")]

    operations = [
        migrations.CreateModel(
            name="PersonKey",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("active", models.BooleanField(default=True)),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="creation time"
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name="last modification time"
                    ),
                ),
                (
                    "slug",
                    autoslug.fields.AutoSlugField(
                        editable=False,
                        max_length=64,
                        populate_from="verbose_name",
                        unique=True,
                    ),
                ),
                ("verbose_name", models.CharField(max_length=64)),
            ],
            options={"ordering": ["verbose_name"], "base_manager_name": "objects"},
        ),
        migrations.CreateModel(
            name="PersonKeyValue",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("active", models.BooleanField(default=True)),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="creation time"
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name="last modification time"
                    ),
                ),
                ("value", models.CharField(max_length=256)),
                (
                    "key",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="people.PersonKey",
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="people.Person"
                    ),
                ),
            ],
            options={"abstract": False},
        ),
    ]
