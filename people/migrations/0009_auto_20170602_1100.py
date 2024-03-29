# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-02 16:00
from __future__ import unicode_literals

import directory
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("people", "0008_auto_20170306_1402")]

    operations = [
        migrations.AlterModelOptions(
            name="emailaddress",
            options={
                "base_manager_name": "objects",
                "ordering": ["-public", "-preferred", "-verified", "address"],
                "verbose_name_plural": "email addresses",
            },
        ),
        migrations.AlterModelOptions(
            name="person",
            options={
                "base_manager_name": "objects",
                "ordering": ["sn", "given_name"],
                "verbose_name_plural": "people",
            },
        ),
        migrations.AlterModelOptions(
            name="personflag",
            options={"base_manager_name": "objects", "ordering": ["verbose_name"]},
        ),
        migrations.AlterModelOptions(
            name="phonenumber", options={"base_manager_name": "objects"}
        ),
        migrations.AlterModelOptions(
            name="streetaddress",
            options={
                "base_manager_name": "objects",
                "verbose_name_plural": "street addresses",
            },
        ),
        migrations.AlterField(
            model_name="emailaddress",
            name="type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="people.ContactInfoType"
            ),
        ),
        migrations.AlterField(
            model_name="phonenumber",
            name="number",
            field=directory._localflav(max_length=32),
        ),
        migrations.AlterField(
            model_name="phonenumber",
            name="type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="people.ContactInfoType"
            ),
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
        migrations.AlterField(
            model_name="streetaddress",
            name="type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="people.ContactInfoType"
            ),
        ),
    ]
