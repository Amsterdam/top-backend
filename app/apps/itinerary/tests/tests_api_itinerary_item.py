from apps.cases.models import Case
from apps.itinerary.models import Itinerary, ItineraryItem
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.utils.unittest_helpers import (
    get_authenticated_client,
    get_unauthenticated_client,
)


class ItineraryItemViewsCreateTest(APITestCase):
    """
    Tests for the API endpoint for creating Itinerary Items
    """

    def test_unauthenticated_post(self):
        """
        An unauthenticated request should not be possible
        """

        url = reverse("itinerary-item-list")
        client = get_unauthenticated_client()
        response = client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_create(self):
        """
        An authenticated post should create an Itinerary Item
        """
        itinerary = Itinerary.objects.create()
        self.assertEquals([], list(itinerary.items.all()))

        CASE_ID = "FOO CASE ID"

        data = {"itinerary": itinerary.id, "case_id": CASE_ID}

        url = reverse("itinerary-item-list")
        client = get_authenticated_client()
        response = client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        itinerary_items = list(itinerary.items.all())
        self.assertEqual(1, len(itinerary_items))
        self.assertEqual(CASE_ID, itinerary_items[0].case.case_id)

    def test_authenticated_create_with_position(self):
        """
        An authenticated post should create an Itinerary Item
        """
        itinerary = Itinerary.objects.create()
        self.assertEquals([], list(itinerary.items.all()))

        CASE_ID = "FOO CASE ID"
        POSITION = 1.234567

        data = {"itinerary": itinerary.id, "case_id": CASE_ID, "position": POSITION}

        url = reverse("itinerary-item-list")
        client = get_authenticated_client()
        response = client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        itinerary_items = list(itinerary.items.all())
        self.assertEqual(POSITION, itinerary_items[0].position)


class ItineraryItemViewsDeleteTest(APITestCase):
    """
    Tests for the API endpoint for deleting Itinerary Items
    """

    def test_unauthenticated_delete(self):
        """
        An unauthenticated request should not be possible
        """

        url = reverse("itinerary-item-detail", kwargs={"pk": "foo"})
        client = get_unauthenticated_client()
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_delete(self):
        """
        An authenticated post should delete an Itinerary Item
        """
        itinerary = Itinerary.objects.create()
        case = Case.get("FOO Case ID")
        itinerary_item = ItineraryItem.objects.create(itinerary=itinerary, case=case)

        self.assertEqual(1, len(itinerary.items.all()))

        url = reverse("itinerary-item-detail", kwargs={"pk": itinerary_item.id})
        client = get_authenticated_client()
        response = client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(0, len(itinerary.items.all()))


class ItineraryItemViewsUpdateTest(APITestCase):
    """
    Tests for the API endpoint for updating Itinerary Items
    """

    def test_unauthenticated_update(self):
        """
        An unauthenticated request should not be possible
        """

        url = reverse("itinerary-item-detail", kwargs={"pk": "foo"})
        client = get_unauthenticated_client()
        response = client.put(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_update(self):
        """
        Update the item's position
        """
        itinerary = Itinerary.objects.create()
        case = Case.get("FOO Case ID")
        itinerary_item = ItineraryItem.objects.create(
            itinerary=itinerary, case=case, position=0
        )

        url = reverse("itinerary-item-detail", kwargs={"pk": itinerary_item.id})
        client = get_authenticated_client()

        NEW_POSITION = 1
        data = {"position": NEW_POSITION}
        response = client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        itinerary_item = ItineraryItem.objects.get(id=itinerary_item.id)
        self.assertEqual(itinerary_item.position, NEW_POSITION)

    def test_authenticated_update_check(self):
        """
        Update the item's checked status
        """

        itinerary = Itinerary.objects.create()
        case = Case.get("FOO Case ID")
        itinerary_item = ItineraryItem.objects.create(
            itinerary=itinerary, case=case, checked=False
        )

        url = reverse("itinerary-item-detail", kwargs={"pk": itinerary_item.id})
        client = get_authenticated_client()

        data = {"checked": True}
        response = client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        itinerary_item = ItineraryItem.objects.get(id=itinerary_item.id)
        self.assertEqual(itinerary_item.checked, True)
