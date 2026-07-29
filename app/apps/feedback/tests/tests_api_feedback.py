import requests_mock
from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from utils.unittest_helpers import get_authenticated_client, get_unauthenticated_client

ZAKEN_API_URL = "https://aza.nl"


class FeedbackViewTest(APITestCase):
    """
    Tests for the feedback proxy endpoint
    """

    def test_unauthenticated_post(self):
        """
        An unauthenticated request should not be possible
        """
        url = reverse("v1:feedback")
        client = get_unauthenticated_client()
        response = client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_post_missing_fields(self):
        """
        A request missing required fields should not be forwarded
        """
        url = reverse("v1:feedback")
        client = get_authenticated_client()
        response = client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(ZAKEN_API_URL=ZAKEN_API_URL)
    @requests_mock.Mocker()
    def test_authenticated_post_forwards_to_zaken(self, m):
        """
        A valid, authenticated request should be forwarded to the Zaken backend
        """
        m.post(f"{settings.ZAKEN_API_URL}/feedback/", status_code=200)

        data = {
            "feedback": "Dit werkt niet zoals verwacht",
            "url": "https://top.nl/some/page",
            "user_agent": "Mozilla/5.0",
            "screen": "1920x1080",
        }

        url = reverse("v1:feedback")
        client = get_authenticated_client()
        response = client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(m.call_count, 1)
        self.assertEqual(m.last_request.json(), {**data, "app_name": "TOP"})

    @override_settings(ZAKEN_API_URL=ZAKEN_API_URL)
    @requests_mock.Mocker()
    def test_authenticated_post_propagates_zaken_error(self, m):
        """
        An error response from the Zaken backend should raise (and result in a 500)
        """
        m.post(f"{settings.ZAKEN_API_URL}/feedback/", status_code=500)

        data = {
            "feedback": "Dit werkt niet zoals verwacht",
            "url": "https://top.amsterdam.nl/some/page",
        }

        url = reverse("v1:feedback")
        client = get_authenticated_client()
        client.raise_request_exception = False
        response = client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
