# Generated by Django 3.2.13 on 2022-05-02 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("visits", "0016_auto_20210303_1504"),
    ]

    operations = [
        migrations.AddField(
            model_name="visit",
            name="completed",
            field=models.BooleanField(default=True),
        ),
    ]
