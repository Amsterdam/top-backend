# Generated by Django 2.1.11 on 2019-11-20 10:39

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("cases", "0004_auto_20191119_2146"),
    ]

    operations = [
        migrations.RenameField(
            model_name="case",
            old_name="stadium",
            new_name="stadium_code",
        ),
    ]
