# Generated by Django 3.1.2 on 2021-03-16 20:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planner", "0022_teamsettings_use_zaken_backend"),
    ]

    operations = [
        migrations.AddField(
            model_name="teamsettings",
            name="zaken_team_name",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
