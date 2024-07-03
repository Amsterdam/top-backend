from apps.itinerary.models import Itinerary, PostalCodeSettings
from django.conf import settings
from django.test import TestCase


class ItinerarySettingsModelTest(TestCase):
    def test_with_postal_code_range(self):
        """
        Test creating with postal code range
        """
        itinerary = Itinerary.objects.create()
        FOO_MIN_RANGE = settings.CITY_MIN_POSTAL_CODE
        FOO_MAX_RANGE = settings.CITY_MAX_POSTAL_CODE

        postal_code_range = PostalCodeSettings.objects.create(
            itinerary=itinerary, range_start=FOO_MIN_RANGE, range_end=FOO_MAX_RANGE
        )
        postal_code_range.clean()
        self.assertEquals(PostalCodeSettings.objects.count(), 1)

    def test_with_postal_code_range_fail(self):
        """
        Should fail if the range_start is larger than the range_end
        """
        itinerary = Itinerary.objects.create()
        FOO_MIN_RANGE = settings.CITY_MIN_POSTAL_CODE

        with self.assertRaises(Exception):
            postal_code_range = PostalCodeSettings.objects.create(
                itinerary=itinerary,
                range_start=FOO_MIN_RANGE,
                range_end=FOO_MIN_RANGE - 1,
            )
            postal_code_range.clean()

    def test_with_postal_code_range_fail_missing_range_end(self):
        """
        Should fail if the range_end is missing
        """
        itinerary = Itinerary.objects.create()
        FOO_MIN_RANGE = settings.CITY_MIN_POSTAL_CODE

        with self.assertRaises(Exception):
            postal_code_range = PostalCodeSettings.objects.create(
                itinerary=itinerary,
                range_start=FOO_MIN_RANGE,
            )
            postal_code_range.clean()

    def test_with_postal_code_range_fail_missing_range_start(self):
        """
        Should fail if the range_end is missing
        """
        itinerary = Itinerary.objects.create()
        FOO_MAX_RANGE = settings.CITY_MAX_POSTAL_CODE

        with self.assertRaises(Exception):
            postal_code_range = PostalCodeSettings.objects.create(
                itinerary=itinerary,
                range_end=FOO_MAX_RANGE,
            )
            postal_code_range.clean()

    def test_reverse_access(self):
        """
        Multiple postal code ranges should be accessible through the ItinerarySettings object
        """
        itinerary = Itinerary.objects.create()
        FOO_MIN_RANGE = settings.CITY_MIN_POSTAL_CODE
        FOO_MAX_RANGE = settings.CITY_MAX_POSTAL_CODE
        N_RANGES = 4

        for i in range(N_RANGES):
            postal_code_range = PostalCodeSettings.objects.create(
                itinerary=itinerary,
                range_start=FOO_MIN_RANGE + i,
                range_end=FOO_MAX_RANGE,
            )
            postal_code_range.clean()

        self.assertEqual(itinerary.postal_code_settings.count(), N_RANGES)
