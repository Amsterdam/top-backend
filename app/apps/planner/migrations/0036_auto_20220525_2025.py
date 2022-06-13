# Generated by Django 3.2.13 on 2022-05-25 18:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("planner", "0035_daysettings_housing_corporation_combiteam"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="daysettings",
            name="exclude_stadia",
        ),
        migrations.RemoveField(
            model_name="daysettings",
            name="primary_stadium",
        ),
        migrations.RemoveField(
            model_name="daysettings",
            name="projects",
        ),
        migrations.RemoveField(
            model_name="daysettings",
            name="secondary_stadia",
        ),
        migrations.RemoveField(
            model_name="daysettings",
            name="sia_presedence",
        ),
        migrations.RemoveField(
            model_name="teamsettings",
            name="is_sia_weights",
        ),
        migrations.RemoveField(
            model_name="teamsettings",
            name="marked_stadia",
        ),
        migrations.RemoveField(
            model_name="teamsettings",
            name="project_choices",
        ),
        migrations.RemoveField(
            model_name="teamsettings",
            name="show_issuemelding",
        ),
        migrations.RemoveField(
            model_name="teamsettings",
            name="show_vakantieverhuur",
        ),
        migrations.RemoveField(
            model_name="teamsettings",
            name="stadia_choices",
        ),
        migrations.RemoveField(
            model_name="weights",
            name="is_sia",
        ),
        migrations.RemoveField(
            model_name="weights",
            name="issuemelding",
        ),
        migrations.RemoveField(
            model_name="weights",
            name="primary_stadium",
        ),
        migrations.RemoveField(
            model_name="weights",
            name="reason",
        ),
        migrations.RemoveField(
            model_name="weights",
            name="secondary_stadium",
        ),
        migrations.RemoveField(
            model_name="weights",
            name="state_types",
        ),
    ]