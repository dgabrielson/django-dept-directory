# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-02 15:55
from __future__ import unicode_literals

import directory
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("directory", "0005_auto_20160126_1350")]

    operations = [
        migrations.AlterModelOptions(
            name="directoryentry",
            options={
                "base_manager_name": "objects",
                "ordering": ["type", "ordering", "person"],
                "verbose_name_plural": "directory entries",
            },
        ),
        migrations.AlterModelOptions(
            name="entrytype",
            options={
                "base_manager_name": "objects",
                "ordering": ["ordering", "verbose_name"],
            },
        ),
        migrations.AlterField(
            model_name="directoryentry",
            name="office",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="places.Office",
            ),
        ),
        migrations.AlterField(
            model_name="directoryentry",
            name="phone_number",
            field=directory._localflav(
                blank=True,
                default=b"",
                help_text=b"(Optional) if not given, the office's phone number will be used.",
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="directoryentry",
            name="type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="directory.EntryType"
            ),
        ),
    ]