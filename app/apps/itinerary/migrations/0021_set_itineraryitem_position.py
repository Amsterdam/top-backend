from django.db import migrations


def set_positions(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    ItineraryItem = apps.get_model("itinerary", "ItineraryItem")

    itinerary_items = ItineraryItem.objects.all()

    # Populate each item with a position
    for index, item in enumerate(itinerary_items):
        item.position = index
        item.save()


class Migration(migrations.Migration):
    dependencies = [
        ("itinerary", "0020_itineraryitem_position"),
    ]

    operations = [
        migrations.RunPython(set_positions),
    ]
