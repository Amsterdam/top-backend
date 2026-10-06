from apps.cases.models import Case
from apps.itinerary.models import Itinerary, ItinerarySettings
from django.test import TestCase


class ItinerarySettingsModelTest(TestCase):
    def get_new_itinerary_settings(self):
        """
        Helper function to create basic new ItinerarySettings object
        """
        itinerary = Itinerary.objects.create()
        return ItinerarySettings.objects.create(
            opening_date="2020-04-04", itinerary=itinerary
        )

    def test_create_itinerary_settings(self):
        """
        ItinerarySettings can be created
        """
        self.assertEqual(ItinerarySettings.objects.count(), 0)
        self.get_new_itinerary_settings()
        self.assertEqual(ItinerarySettings.objects.count(), 1)

    def test_target_length_default(self):
        """
        Target length should default to 8
        """
        itinerary_settings = self.get_new_itinerary_settings()
        self.assertEqual(8, itinerary_settings.target_length)

    def test_create_with_start_case(self):
        """
        Test creating with start_case
        """
        self.assertEqual(ItinerarySettings.objects.count(), 0)
        itinerary = Itinerary.objects.create()
        case = Case.get("FOO_CASE_ID")

        ItinerarySettings.objects.create(
            opening_date="2020-04-04", itinerary=itinerary, start_case=case
        )
        self.assertEqual(ItinerarySettings.objects.count(), 1)
