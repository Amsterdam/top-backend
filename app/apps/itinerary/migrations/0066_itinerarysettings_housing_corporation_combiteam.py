# Generated by Django 3.2 on 2022-03-28 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("itinerary", "0065_auto_20220314_1425"),
    ]

    operations = [
        migrations.AddField(
            model_name="itinerarysettings",
            name="housing_corporation_combiteam",
            field=models.BooleanField(default=False),
        ),
    ]
