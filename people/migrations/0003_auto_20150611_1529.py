# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("people", "0002_auto_20141014_0810")]

    operations = [
        migrations.AlterField(
            model_name="emailconfirmation",
            name="email",
            field=models.OneToOneField(
                on_delete=models.deletion.CASCADE, to="people.EmailAddress"
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="flags",
            field=models.ManyToManyField(to="people.PersonFlag", blank=True),
        ),
    ]
