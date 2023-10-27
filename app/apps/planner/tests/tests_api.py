from apps.planner.models import DaySettings, TeamSettings
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from app.utils.unittest_helpers import (
    get_authenticated_client,
    get_unauthenticated_client,
)


class TeamSettingsViewSet(APITestCase):
    """
    Tests for the API endpoints for retrieving team settings
    """

    def get_url(self):
        return reverse("v1:team-settings-list")

    def test_unauthenticated_request(self):
        """
        An unauthenticated request should not be possible
        """

        url = self.get_url()
        client = get_unauthenticated_client()
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_requests(self):
        """
        An authenticated request should be possible
        """

        client = get_authenticated_client()
        response = client.get(self.get_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get("results")), 0)

    def test_authenticated_requests_two_team_settings(self):
        """
        An authenticated request should be possible
        """

        baker.make(TeamSettings)
        baker.make(TeamSettings)

        client = get_authenticated_client()
        response = client.get(self.get_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get("results")), 2)


class DaySettingsViewSet(APITestCase):
    """
    Tests for the API endpoints for retrieving day settings
    """

    def get_url(self):
        return reverse("v1:day-settings-list")

    def test_unauthenticated_request(self):
        """
        An unauthenticated request should not be possible
        """

        url = self.get_url()
        client = get_unauthenticated_client()
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_requests(self):
        """
        An authenticated request should be possible
        """

        client = get_authenticated_client()
        response = client.get(self.get_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get("results")), 0)

    def test_authenticated_requests_get_day_settings(self):
        """
        An authenticated request should be possible
        """

        DAY_SETTINGS_ID = 1
        DAY_SETTINGS_NAME = "FOO_NAME"
        team_settings_1 = baker.make(TeamSettings)
        baker.make(
            DaySettings,
            team_settings=team_settings_1,
            id=DAY_SETTINGS_ID,
            name=DAY_SETTINGS_NAME,
        )

        client = get_authenticated_client()
        response = client.get(reverse("v1:day-settings-detail", kwargs={"pk": 1}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("name"), DAY_SETTINGS_NAME)

    def test_authenticated_requests_update_day_settings(self):
        """
        An authenticated request should be possible
        """

        DAY_SETTINGS_ID = 1
        DAY_SETTINGS_NAME = "FOO_NAME"
        team_settings_1 = baker.make(TeamSettings)
        baker.make(
            DaySettings,
            team_settings=team_settings_1,
            id=DAY_SETTINGS_ID,
            name=DAY_SETTINGS_NAME,
        )

        client = get_authenticated_client()
        response = client.get(reverse("v1:day-settings-detail", kwargs={"pk": 1}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("name"), DAY_SETTINGS_NAME)


class DaySettingsUpdateTestViewSet(APITestCase):
    """
    Tests for the API endpoints for retrieving day settings
    """

    def test_unauthenticated_update(self):
        """
        An unauthenticated request should not be possible
        """

        url = reverse("v1:day-settings-detail", kwargs={"pk": "foo"})
        client = get_unauthenticated_client()
        response = client.put(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_put(self):
        """
        An unauthenticated request should not be possible
        """
        DAY_SETTINGS_ID = 1
        DAY_SETTINGS_NAME = "FOO_NAME"
        team_settings_1 = baker.make(TeamSettings)
        baker.make(
            DaySettings,
            team_settings=team_settings_1,
            id=DAY_SETTINGS_ID,
            name=DAY_SETTINGS_NAME,
        )

        url = reverse("v1:day-settings-detail", kwargs={"pk": DAY_SETTINGS_ID})
        client = get_unauthenticated_client()
        response = client.put(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_update_empty_payload(self):
        """
        An authenticated request should be possible
        """

        DAY_SETTINGS_ID = 1
        DAY_SETTINGS_NAME = "FOO_NAME"
        team_settings_1 = baker.make(TeamSettings)
        baker.make(
            DaySettings,
            team_settings=team_settings_1,
            id=DAY_SETTINGS_ID,
            name=DAY_SETTINGS_NAME,
        )

        url = reverse("v1:day-settings-detail", kwargs={"pk": DAY_SETTINGS_ID})

        client = get_authenticated_client()
        response = client.put(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertEqual(response.json().get("name"), DAY_SETTINGS_NAME)
