# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("person_tags", "0001_initial")]

    operations = [
        migrations.AlterModelOptions(
            name="persontaggedentry",
            options={
                "ordering": ["person", "ordering", "tag"],
                "verbose_name_plural": "Person Tagged Entries",
            },
        )
    ]
