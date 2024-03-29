# Generated by Django 3.1.2 on 2021-04-06 16:21

import django.contrib.postgres.fields
from django.db import migrations, models


def move_days_to_days_list(apps, schema_editor):
    DaySettings = apps.get_model("planner", "DaySettings")
    for daySettings in DaySettings.objects.all():
        daySettings.week_days = (
            [daySettings.week_day] if daySettings.week_day is not None else []
        )
        daySettings.save()


class Migration(migrations.Migration):

    dependencies = [
        ("planner", "0027_auto_20210330_1207"),
    ]

    operations = [
        migrations.AddField(
            model_name="daysettings",
            name="week_days",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.PositiveSmallIntegerField(),
                blank=True,
                null=True,
                size=None,
            ),
        ),
        migrations.RunPython(move_days_to_days_list),
    ]
