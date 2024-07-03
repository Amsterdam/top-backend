# Generated by Django 3.1 on 2020-10-28 12:33

import apps.planner.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planner", "0005_teamsettings_marked_stadia"),
    ]

    operations = [
        migrations.AlterField(
            model_name="teamsettings",
            name="settings",
            field=models.JSONField(
                default=apps.planner.models.team_settings_settings_default
            ),
        ),
    ]
