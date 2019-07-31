# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("directory", "0002_auto_20150611_1109")]

    operations = [
        migrations.AddField(
            model_name="directoryentry",
            name="description",
            field=models.CharField(
                default=b"",
                help_text=b"(Optional) only used on personal pages to distinguish multiple offices.",
                max_length=200,
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="directoryentry",
            name="phone_number",
            field=models.CharField(
                default=b"",
                help_text=b"(Optional) if not given, the office's phone number will be used.",
                max_length=32,
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="directoryentry",
            name="title",
            field=models.CharField(
                help_text=b"(Optional) if not given, the person's title will be used.",
                max_length=64,
                blank=True,
            ),
        ),
    ]
