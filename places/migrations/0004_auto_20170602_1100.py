# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-02 16:00
from __future__ import unicode_literals

import directory
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("places", "0003_auto_20160126_1350")]

    operations = [
        migrations.AlterField(
            model_name="office",
            name="phone_number",
            field=directory._localflav(blank=True, max_length=32),
        )
    ]
