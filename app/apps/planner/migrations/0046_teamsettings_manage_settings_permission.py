from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("planner", "0045_alter_daysettings_housing_corporation_combiteam"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="teamsettings",
            options={
                "ordering": ["name"],
                "permissions": [("manage_settings", "Can manage settings")],
                "verbose_name_plural": "Team settings",
            },
        ),
    ]
