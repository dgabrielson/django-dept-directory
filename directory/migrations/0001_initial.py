# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("places", "0001_initial"), ("people", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="DirectoryEntry",
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
                (
                    "title",
                    models.CharField(
                        help_text=b"If not given, the person's title will be used.",
                        max_length=64,
                        blank=True,
                    ),
                ),
                (
                    "url",
                    models.CharField(
                        help_text=b"(Optional) if not given, the person's url will be used.",
                        max_length=64,
                        verbose_name=b"URL",
                        blank=True,
                    ),
                ),
                (
                    "mugshot",
                    models.ImageField(
                        help_text=b"(Optional) a photo for the visual directory.",
                        max_length=512,
                        null=True,
                        upload_to=b"directory/faces/%Y/%m",
                        blank=True,
                    ),
                ),
                (
                    "note",
                    models.CharField(
                        help_text=b"(Optional) a short note about e.g., being on leave.",
                        max_length=200,
                        null=True,
                        blank=True,
                    ),
                ),
                ("ordering", models.PositiveSmallIntegerField(default=100)),
                (
                    "office",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        blank=True,
                        to="places.Office",
                        null=True,
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        help_text=b'Only people with the "directory" flag are shown',
                        to="people.Person",
                    ),
                ),
            ],
            options={
                "ordering": ["ordering", "person", "type"],
                "verbose_name_plural": "directory entries",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="EntryType",
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
                ("verbose_name", models.CharField(max_length=64)),
                ("verbose_name_plural", models.CharField(max_length=64)),
                ("ordering", models.PositiveSmallIntegerField(default=10)),
            ],
            options={"ordering": ["ordering", "verbose_name"]},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="directoryentry",
            name="type",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE, to="directory.EntryType"
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="directoryentry", unique_together=set([("person", "type")])
        ),
    ]
