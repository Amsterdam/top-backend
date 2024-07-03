# Generated by Django 3.0.7 on 2020-08-10 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("visits", "0004_auto_20200806_1121"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="visit",
            name="suggest_visit_next_time",
        ),
        migrations.AddField(
            model_name="visit",
            name="can_next_visit_go_ahead",
            field=models.BooleanField(blank=True, default=True, null=True),
        ),
        migrations.AddField(
            model_name="visit",
            name="next_visit_can_go_ahead_description",
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name="visit",
            name="personal_notes",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="visit",
            name="suggest_next_visit_description",
            field=models.TextField(blank=True, null=True),
        ),
    ]
