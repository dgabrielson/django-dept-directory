# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("people", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="PersonTag",
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
                ("slug", models.SlugField(unique=True, max_length=255)),
                ("tag", models.CharField(max_length=255)),
            ],
            options={"ordering": ["tag"]},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PersonTaggedEntry",
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
                ("ordering", models.PositiveSmallIntegerField(default=0)),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE, to="people.Person"
                    ),
                ),
                (
                    "tag",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE, to="person_tags.PersonTag"
                    ),
                ),
            ],
            options={
                "ordering": ["ordering", "tag"],
                "verbose_name_plural": "Person Tagged Entries",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="TagGroup",
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
                ("name", models.CharField(max_length=64)),
                ("slug", models.SlugField(unique=True, max_length=64)),
                ("description", models.TextField(blank=True)),
                (
                    "tags",
                    models.ManyToManyField(to="person_tags.PersonTag", blank=True),
                ),
            ],
            options={"ordering": ["name"]},
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name="persontaggedentry", unique_together=set([("person", "tag")])
        ),
    ]
