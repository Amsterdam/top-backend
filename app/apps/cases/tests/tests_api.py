import datetime

from apps.cases.models import Case
from apps.itinerary.models import ItineraryItem
from apps.visits.models import Visit
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from app.utils.unittest_helpers import (
    get_authenticated_client,
    get_unauthenticated_client,
)


class CaseViewSetTest(APITestCase):
    """
    Tests for the API endpoints for retrieving case data
    """

    def test_unauthenticated_request(self):
        """
        An unauthenticated request should not be possible
        """

        url = reverse("v1:case-detail", kwargs={"pk": "foo"})
        client = get_unauthenticated_client()
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_all_visits_timeline(self):
        datetime_now = datetime.datetime.now()
        datetime_future = datetime.datetime.now() + datetime.timedelta(hours=1)

        case = baker.make(Case, case_id="test")

        itinerary_item = baker.make(ItineraryItem, case=case)
        baker.make(
            Visit, itinerary_item=itinerary_item, start_time=datetime_now, case_id=case
        )
        baker.make(
            Visit,
            itinerary_item=itinerary_item,
            start_time=datetime_future,
            case_id=case,
        )

        url = reverse("v1:case-visits", kwargs={"pk": case.case_id})
        client = get_authenticated_client()
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    def test_ordering_get_all_visits_timeline(self):
        datetime_now = datetime.datetime.now()
        datetime_future = datetime.datetime.now() + datetime.timedelta(hours=1)

        case = baker.make(Case, case_id="test")
        itinerary_item = baker.make(ItineraryItem, case=case)
        visit_1 = baker.make(
            Visit, itinerary_item=itinerary_item, start_time=datetime_now, case_id=case
        )
        visit_2 = baker.make(
            Visit,
            itinerary_item=itinerary_item,
            start_time=datetime_future,
            case_id=case,
        )

        url = reverse("v1:case-visits", kwargs={"pk": case.case_id})
        client = get_authenticated_client()
        response = client.get(url)
        self.assertEqual(response.json()[0]["id"], visit_2.id)
        self.assertEqual(response.json()[1]["id"], visit_1.id)


class CaseSearchViewSetTest(APITestCase):
    """
    Tests for the API endpoint for searching cases
    """

    MOCK_SEARCH_QUERY_PARAMETERS = {
        "postalCode": "FOO_POSTAL_CODE",
        "streetNumber": "FOO_STREET_NUMBER",
        "suffix": "FOO_SUFFIX",
        "streetName": "FOO_STREET_NAME",
    }

    def test_unauthenticated_request(self):
        """
        An unauthenticated search should not be possible
        """
        url = reverse("v1:search-list")
        client = get_unauthenticated_client()
        response = client.get(url, self.MOCK_SEARCH_QUERY_PARAMETERS)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
