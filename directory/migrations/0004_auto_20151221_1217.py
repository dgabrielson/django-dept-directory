# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-21 18:17
from __future__ import unicode_literals

import directory
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("directory", "0003_auto_20151113_1307")]

    operations = [
        migrations.AlterField(
            model_name="directoryentry",
            name="phone_number",
            field=directory._localflav(
                blank=True,
                default=b"",
                help_text=b"(Optional) if not given, the office's phone number will be used.",
                max_length=32,
            ),
        )
    ]