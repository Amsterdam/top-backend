# Generated by Django 3.0.7 on 2020-07-24 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("visits", "0002_visit_cooperation"),
    ]

    operations = [
        migrations.AddField(
            model_name="visit",
            name="no_cooperation",
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name="visit",
            name="nobody_present",
            field=models.BooleanField(null=True),
        ),
    ]
