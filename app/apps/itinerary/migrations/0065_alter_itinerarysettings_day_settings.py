# Generated by Django 3.2 on 2021-11-10 10:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planner", "0032_teamsettings_fraudprediction_pilot_enabled"),
        ("itinerary", "0064_alter_itinerarysettings_start_case"),
    ]

    operations = [
        migrations.AlterField(
            model_name="itinerarysettings",
            name="day_settings",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="itinerary_day_settings",
                to="planner.daysettings",
            ),
        ),
    ]
