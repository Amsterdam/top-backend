from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("planner", "0041_add_subjects_tags_daysetting_itinerary"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="teamsettings",
            name="fraudprediction_pilot_enabled",
        ),
        migrations.RemoveField(
            model_name="teamsettings",
            name="fraud_prediction_model",
        ),
    ]
