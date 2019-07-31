# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-20 15:48
from __future__ import unicode_literals

import directory
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("people", "0012_auto_20170919_1504")]

    operations = [
        migrations.AlterModelOptions(
            name="personkey",
            options={
                "base_manager_name": "objects",
                "ordering": ["verbose_name"],
                "verbose_name": "Additional person field",
            },
        ),
        migrations.AlterModelOptions(
            name="personkeyvalue",
            options={
                "base_manager_name": "objects",
                "verbose_name": "Additional data",
                "verbose_name_plural": "Additional data",
            },
        ),
        migrations.AlterField(
            model_name="personkeyvalue",
            name="key",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="people.PersonKey",
                verbose_name="Field",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="personkeyvalue", unique_together=set([("person", "key")])
        ),
    ]