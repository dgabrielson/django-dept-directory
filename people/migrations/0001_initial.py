# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ContactInfoType",
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
                ("slug", models.SlugField(max_length=32)),
                ("verbose_name", models.CharField(max_length=32)),
                ("verbose_name_plural", models.CharField(max_length=32)),
            ],
            options={"ordering": ["verbose_name"]},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="EmailAddress",
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
                ("public", models.BooleanField(default=False)),
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
                ("preferred", models.BooleanField(default=False)),
                ("verified", models.BooleanField(default=False)),
                ("address", models.EmailField(max_length=128)),
            ],
            options={
                "ordering": ["-public", "-preferred", "-verified", "address"],
                "verbose_name_plural": "email addresses",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="EmailConfirmation",
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
                ("key", models.CharField(max_length=64)),
                (
                    "email_send_time",
                    models.DateTimeField(
                        help_text=b"If this is not set, the verification email has <em>not</em> been sent.",
                        null=True,
                    ),
                ),
                ("redirect_url", models.URLField(blank=True)),
                (
                    "delete_unverified",
                    models.BooleanField(
                        default=False,
                        help_text=b"If this is set, unverified email addresses and people objects will be deleted",
                    ),
                ),
                (
                    "email",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        to="people.EmailAddress",
                        unique=True,
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Person",
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
                    "cn",
                    models.CharField(
                        help_text=b"This is how the person's name will appear in the site.\n                                    Leave this blank to use given name + family name.\n                                    ",
                        max_length=100,
                        verbose_name=b"common name",
                        blank=True,
                    ),
                ),
                (
                    "sn",
                    models.CharField(
                        help_text=b"This will determine how this person gets sorted in lists or people.",
                        max_length=64,
                        verbose_name=b"family name",
                    ),
                ),
                (
                    "given_name",
                    models.CharField(
                        help_text=b"Typically how the person prefers to be addressed, informally.",
                        max_length=64,
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text=b"A personal title or job title.",
                        max_length=64,
                        blank=True,
                    ),
                ),
                (
                    "company",
                    models.CharField(
                        help_text=b"The company this person if affiliated with.",
                        max_length=64,
                        blank=True,
                    ),
                ),
                (
                    "birthday",
                    models.DateField(
                        help_text=b"If this is not required, just leave this blank.",
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "username",
                    models.CharField(
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
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        null=True,
                        blank=True,
                        help_text=b"A url fragment for this person, if required.",
                        unique=True,
                    ),
                ),
                ("note", models.TextField(blank=True)),
            ],
            options={"ordering": ["sn", "given_name"], "verbose_name_plural": "people"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PersonFlag",
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
            ],
            options={"ordering": ["verbose_name"]},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PhoneNumber",
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
                ("public", models.BooleanField(default=False)),
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
                ("preferred", models.BooleanField(default=False)),
                ("verified", models.BooleanField(default=False)),
                ("number", models.CharField(max_length=32)),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE, to="people.Person"
                    ),
                ),
                (
                    "type",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE, to="people.ContactInfoType"
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="StreetAddress",
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
                ("public", models.BooleanField(default=False)),
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
                ("preferred", models.BooleanField(default=False)),
                ("verified", models.BooleanField(default=False)),
                ("street_1", models.CharField(max_length=128, blank=True)),
                (
                    "street_2",
                    models.CharField(help_text=b"Optional", max_length=128, blank=True),
                ),
                (
                    "city",
                    models.CharField(
                        help_text=b"(Township, Municipality, etc.)",
                        max_length=64,
                        blank=True,
                    ),
                ),
                (
                    "region",
                    models.CharField(
                        help_text=b"Provinces in Canada, States for U.S.A.",
                        max_length=64,
                        blank=True,
                    ),
                ),
                ("country", models.CharField(max_length=64, blank=True)),
                ("postal_code", models.CharField(max_length=16, blank=True)),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE, to="people.Person"
                    ),
                ),
                (
                    "type",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE, to="people.ContactInfoType"
                    ),
                ),
            ],
            options={"verbose_name_plural": "street addresses"},
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name="phonenumber", unique_together=set([("person", "number")])
        ),
        migrations.AddField(
            model_name="person",
            name="flags",
            field=models.ManyToManyField(to="people.PersonFlag", null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="emailaddress",
            name="person",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE, to="people.Person"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="emailaddress",
            name="type",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE, to="people.ContactInfoType"
            ),
            preserve_default=True,
        ),
    ]
