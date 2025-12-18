from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("planner", "0042_remove_fraud_fields"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="daysettings",
            name="week_day",
        ),
    ]
