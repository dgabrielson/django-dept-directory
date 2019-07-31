# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-21 17:10
from __future__ import unicode_literals

import directory
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("people", "0003_auto_20150611_1529")]

    operations = [
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
                help_text=b"Provinces in Canada, States for U.S.A.",
                max_length=64,
            ),
        ),
    ]
