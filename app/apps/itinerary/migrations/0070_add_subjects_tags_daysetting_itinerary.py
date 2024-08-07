# Generated by Django 3.2.13 on 2024-05-14 10:04

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("itinerary", "0069_itinerarysettings_districts"),
    ]

    operations = [
        migrations.AddField(
            model_name="itinerarysettings",
            name="subjects",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.PositiveSmallIntegerField(),
                blank=True,
                null=True,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="itinerarysettings",
            name="tags",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.PositiveSmallIntegerField(),
                blank=True,
                null=True,
                size=None,
            ),
        ),
    ]
