# Generated by Django 2.1.11 on 2019-11-13 15:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("itinerary", "0010_auto_20191111_1557"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="itinerary",
            options={"ordering": ["-date"]},
        ),
    ]
