# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-11 15:02
from __future__ import unicode_literals

import directory
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("people", "0013_auto_20170920_1048")]

    operations = [
        migrations.AlterModelOptions(
            name="personkey",
            options={
                "base_manager_name": "objects",
                "ordering": ["verbose_name"],
                "verbose_name": "additional person field",
            },
        ),
        migrations.AlterModelOptions(
            name="personkeyvalue",
            options={
                "base_manager_name": "objects",
                "verbose_name": "additional data",
                "verbose_name_plural": "additional data",
            },
        ),
        migrations.AlterField(
            model_name="phonenumber",
            name="number",
            field=directory._localflav(max_length=32),
        ),
        migrations.AlterField(
            model_name="streetaddress",
            name="postal_code",
            field=directory._localflav(blank=True, max_length=16),
        ),
        migrations.AlterField(
            model_name="streetaddress",
            name="region",
            field=directory._localflav(
                blank=True,
                help_text="Provinces in Canada, States for U.S.A.",
                max_length=64,
            ),
        ),
    ]