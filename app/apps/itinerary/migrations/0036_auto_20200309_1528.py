# Generated by Django 2.2.10 on 2020-03-09 15:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cases", "0009_auto_20200309_1525"),
        ("itinerary", "0035_auto_20200309_1525"),
    ]

    operations = [
        migrations.RemoveField(model_name="itinerarysettings", name="exclude_stadium",),
        migrations.AddField(
            model_name="itinerarysettings",
            name="exclude_stadia",
            field=models.ManyToManyField(
                related_name="settings_as_exclude_stadia", to="cases.Stadium"
            ),
        ),
        migrations.AlterField(
            model_name="itinerarysettings",
            name="secondary_stadia",
            field=models.ManyToManyField(
                related_name="settings_as_secondary_stadia", to="cases.Stadium"
            ),
        ),
    ]