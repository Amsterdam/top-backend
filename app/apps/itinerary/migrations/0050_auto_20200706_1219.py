# Generated by Django 3.0.7 on 2020-07-06 12:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("itinerary", "0049_remove_postalcodesettings_itinerary_settings"),
    ]

    operations = [
        migrations.AlterField(
            model_name="postalcodesettings",
            name="postal_code_range_end",
            field=models.IntegerField(
                default=0,
                validators=[
                    django.core.validators.MinValueValidator(1000),
                    django.core.validators.MaxValueValidator(1109),
                ],
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="postalcodesettings",
            name="postal_code_range_start",
            field=models.IntegerField(
                default=0,
                validators=[
                    django.core.validators.MinValueValidator(1000),
                    django.core.validators.MaxValueValidator(1109),
                ],
            ),
            preserve_default=False,
        ),
    ]
