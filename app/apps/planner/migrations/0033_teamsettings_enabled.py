# Generated by Django 3.2 on 2021-11-10 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planner", "0032_teamsettings_fraudprediction_pilot_enabled"),
    ]

    operations = [
        migrations.AddField(
            model_name="teamsettings",
            name="enabled",
            field=models.BooleanField(default=True),
        ),
    ]
