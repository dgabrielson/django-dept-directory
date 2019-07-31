# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-12 19:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("person_tags", "0005_auto_20171005_1008")]

    operations = [
        migrations.AlterField(
            model_name="persontag",
            name="tag",
            field=models.CharField(
                help_text="A word or short phrase (only a few words) is best. Do not use capitals except in proper names.",
                max_length=255,
            ),
        )
    ]
