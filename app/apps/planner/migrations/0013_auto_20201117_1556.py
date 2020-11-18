# Generated by Django 3.1.2 on 2020-11-17 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planner", "0012_auto_20201117_1222"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="daysettings",
            options={"ordering": ("week_day", "start_time")},
        ),
        migrations.RemoveField(
            model_name="teamsettings",
            name="team_type",
        ),
        migrations.AddField(
            model_name="teamsettings",
            name="show_issuemelding",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="teamsettings",
            name="show_vakantieverhuur",
            field=models.BooleanField(default=True),
        ),
    ]
