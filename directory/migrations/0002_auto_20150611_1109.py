# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("directory", "0001_initial")]

    operations = [
        migrations.AlterModelOptions(
            name="directoryentry",
            options={
                "ordering": ["type", "ordering", "person"],
                "verbose_name_plural": "directory entries",
            },
        )
    ]
