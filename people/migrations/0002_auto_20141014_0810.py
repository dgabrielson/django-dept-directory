# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("people", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="person",
            name="username",
            field=models.CharField(
                null=True,
                validators=[
                    django.core.validators.RegexValidator(
                        re.compile(b"^[\\w.@+-]+$"),
                        b"Enter a valid username.",
                        b"invalid",
                    )
                ],
                max_length=30,
                blank=True,
                help_text=b"Username on the local system, if the person has one. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters",
                unique=True,
                db_index=True,
            ),
        )
    ]
