# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-21 18:17
from __future__ import unicode_literals

import directory
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("places", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="office",
            name="phone_number",
            field=directory._localflav(blank=True, max_length=32),
        )
    ]
