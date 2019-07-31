# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Room",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("active", models.BooleanField(default=True)),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name=b"creation time"
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name=b"last modification time"
                    ),
                ),
                ("slug", models.SlugField(unique=True, max_length=64)),
                (
                    "number",
                    models.CharField(
                        help_text=b"These are room labels \xe2\x80\x93 not always numeric",
                        max_length=32,
                    ),
                ),
                (
                    "building",
                    models.CharField(
                        help_text=b'Use "-special" to display only the number label for the room',
                        max_length=64,
                    ),
                ),
                (
                    "note",
                    models.CharField(
                        help_text=b"A key serial number, room combination, i>clicker frequency, etc.",
                        max_length=128,
                        blank=True,
                    ),
                ),
            ],
            options={"ordering": ["building", "number"]},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Office",
            fields=[
                (
                    "room_ptr",
                    models.OneToOneField(
                        on_delete=models.deletion.CASCADE,
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="places.Room",
                    ),
                ),
                ("phone_number", models.CharField(max_length=32, blank=True)),
            ],
            options={},
            bases=("places.room",),
        ),
        migrations.CreateModel(
            name="ClassRoom",
            fields=[
                (
                    "room_ptr",
                    models.OneToOneField(
                        on_delete=models.deletion.CASCADE,
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="places.Room",
                    ),
                ),
                ("capacity", models.PositiveSmallIntegerField(null=True, blank=True)),
            ],
            options={},
            bases=("places.room",),
        ),
        migrations.AlterUniqueTogether(
            name="room", unique_together=set([("number", "building")])
        ),
    ]
