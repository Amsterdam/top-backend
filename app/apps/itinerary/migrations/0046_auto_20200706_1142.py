# Generated by Django 3.0.7 on 2020-07-06 11:42

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cases", "0012_auto_20200407_1141"),
        ("itinerary", "0045_auto_20200429_0940"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="itinerarysettings", name="postal_code_range_end",
        ),
        migrations.RemoveField(
            model_name="itinerarysettings", name="postal_code_range_start",
        ),
        migrations.CreateModel(
            name="PostalCodeRange",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "postal_code_range_start",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(1000),
                            django.core.validators.MaxValueValidator(1109),
                        ],
                    ),
                ),
                (
                    "postal_code_range_end",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(1000),
                            django.core.validators.MaxValueValidator(1109),
                        ],
                    ),
                ),
                (
                    "primary_stadium",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="postal_code_ranges",
                        to="cases.Stadium",
                    ),
                ),
            ],
        ),
    ]