import requests_mock
from apps.cases.mock import get_zaken_case_list
from apps.cases.models import Case
from apps.itinerary.models import Itinerary, ItineraryItem
from django.conf import settings
from django.test import override_settings
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

    CASE_ID = "3309"
    zaak = get_zaken_case_list()[0]
    ZAKEN_API_URL = "https://aza.nl"

    def test_unauthenticated_post(self):
        """
        An unauthenticated request should not be possible
        """

        url = reverse("v1:itinerary-item-list")
        client = get_unauthenticated_client()
        response = client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @override_settings(ZAKEN_API_URL=ZAKEN_API_URL)
    @requests_mock.Mocker()
    def test_authenticated_create(self, m):
        """
        An authenticated post should create an Itinerary Item
        """
        m.get(
            f"{settings.ZAKEN_API_URL}/cases/{self.CASE_ID}/?open_cases=True&page_size=1000",
            json=self.zaak,
            status_code=200,
        )
        itinerary = Itinerary.objects.create()
        self.assertEqual([], list(itinerary.items.all()))

        data = {"itinerary": itinerary.id, "id": self.CASE_ID}

        url = reverse("v1:itinerary-item-list")
        client = get_authenticated_client()
        response = client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        itinerary_items = list(itinerary.items.all())
        self.assertEqual(1, len(itinerary_items))
        self.assertEqual(self.CASE_ID, itinerary_items[0].case.case_id)

    @override_settings(ZAKEN_API_URL=ZAKEN_API_URL)
    @requests_mock.Mocker()
    def test_authenticated_create_with_position(self, m):
        """
        An authenticated post should create an Itinerary Item
        """
        m.get(
            f"{settings.ZAKEN_API_URL}/cases/{self.CASE_ID}/?open_cases=True&page_size=1000",
            json=self.zaak,
            status_code=200,
        )
        itinerary = Itinerary.objects.create()
        self.assertEqual([], list(itinerary.items.all()))

        POSITION = 1.234567

        data = {"itinerary": itinerary.id, "id": self.CASE_ID, "position": POSITION}

        url = reverse("v1:itinerary-item-list")

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

        url = reverse("v1:itinerary-item-detail", kwargs={"pk": "foo"})
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

        url = reverse("v1:itinerary-item-detail", kwargs={"pk": itinerary_item.id})
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

        url = reverse("v1:itinerary-item-detail", kwargs={"pk": "foo"})
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

        url = reverse("v1:itinerary-item-detail", kwargs={"pk": itinerary_item.id})
        client = get_authenticated_client()

        NEW_POSITION = 1
        data = {"position": NEW_POSITION}
        response = client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        itinerary_item = ItineraryItem.objects.get(id=itinerary_item.id)
        self.assertEqual(itinerary_item.position, NEW_POSITION)
