# Generated by Django 2.2.2 on 2019-06-04 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("person_tags", "0007_auto_20181130_0810")]

    operations = [
        migrations.AlterField(
            model_name="persontag",
            name="slug",
            field=models.SlugField(
                max_length=255, unique=True, verbose_name="URL fragment"
            ),
        ),
        migrations.AlterField(
            model_name="taggroup",
            name="slug",
            field=models.SlugField(
                max_length=32, unique=True, verbose_name="URL fragment"
            ),
        ),
    ]
