from unittest.mock import patch

from apps.cases.models import Case
from apps.itinerary.models import Itinerary, ItineraryItem
from django.test import TestCase

FOO_CASE_ID_A = "FOO_CASE_ID_A"
FOO_CASE_ID_B = "FOO_CASE_ID_B"
FOO_CASE_C_ID = "FOO_CASE_C_ID"


@patch("django.db.models.signals.ModelSignal.send")
class ItineraryItemModelTest(TestCase):
    def get_itinerary_item(self, mock=None):
        """
        Helper function for tests. Created and returns an ItineraryItem
        """
        itinerary = Itinerary.objects.create()
        case = Case.get(FOO_CASE_ID_A)
        itinerary_item = ItineraryItem.objects.create(itinerary=itinerary, case=case)

        return itinerary_item

    def get_itinerary_items(self, mock=None):
        """
        Helper function for tests. Created and returns multiple ItineraryItems
        """
        itinerary = Itinerary.objects.create()
        case_a = Case.get(FOO_CASE_ID_A)
        itinerary_item_a = ItineraryItem.objects.create(
            itinerary=itinerary, case=case_a
        )

        case_b = Case.get(FOO_CASE_ID_B)
        itinerary_item_b = ItineraryItem.objects.create(
            itinerary=itinerary, case=case_b
        )

        return [itinerary_item_a, itinerary_item_b]

    def test_create_itinerary_item(self, mock):
        """
        ItineraryItem can be created
        """
        self.assertEqual(Itinerary.objects.count(), 0)
        self.get_itinerary_item()
        self.assertEqual(Itinerary.objects.count(), 1)

    def test_string_representation(self, mock):
        """
        __str__ is a case's string
        """
        itinerary_item = self.get_itinerary_item()
        self.assertEqual(FOO_CASE_ID_A, str(itinerary_item))

    def test_set_position_to_last_no_items(self, mock):
        """
        set_position_to_last when no other item's are in the list should be 2
        """

        itinerary_item = self.get_itinerary_item()
        self.assertEqual(itinerary_item.position, 1.0)

        itinerary_item.set_position_to_last()
        self.assertEqual(itinerary_item.position, 2.0)

    def test_set_position_to_last_multiple_items(self, mock):
        """
        set_position_to_last should be last_position + 1
        """
        items = self.get_itinerary_items()
        self.assertEqual(items[0].position, 1)
        self.assertEqual(items[1].position, 2)

        items[0].set_position_to_last()
        self.assertEqual(items[0].position, items[1].position + 1)

    def test_save_no_position(self, mock):
        """
        saving with no position sets the item to the last position
        """
        items = self.get_itinerary_items()
        itinerary = items[0].itinerary

        case_c = Case.get(FOO_CASE_C_ID)
        item = ItineraryItem.objects.create(itinerary=itinerary, case=case_c)

        self.assertEquals(item.position, items[-1].position + 1)

    def test_save_same_position_error(self, mock):
        """
        Saving throws an error if another item has the same position
        """
        items = self.get_itinerary_items()
        itinerary = items[0].itinerary
        case_c = Case.get(FOO_CASE_C_ID)
        same_position = items[0].position

        with self.assertRaises(Exception):
            ItineraryItem.objects.create(
                itinerary=itinerary, case=case_c, position=same_position
            )

    def test_save_same_case_error(self, mock):
        """
        saving throws an error if another item has the same case
        """
        items = self.get_itinerary_items()
        itinerary = items[0].itinerary
        same_case = items[0].case

        with self.assertRaises(Exception):
            ItineraryItem.objects.create(itinerary=itinerary, case=same_case)
