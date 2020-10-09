from constance.test import override_config
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.apps.planner.const import EXAMPLE_PLANNER_SETTINGS
from app.settings.const import ISSUEMELDING, PROJECTS, STADIA
from app.utils.unittest_helpers import (
    get_authenticated_client,
    get_unauthenticated_client,
)


class ConstantsProjectsViewSet(APITestCase):
    """
    Tests for the API endpoints for retrieving project constants
    """

    def get_url(self):
        return reverse("constants-projects-list")

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
        An authenticated request should return the projects constants in a dictionary
        """
        url = self.get_url()
        client = get_authenticated_client()
        response = client.get(url)

        expected_response = {"constants": PROJECTS}
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json(), expected_response)


class ConstantsStadiaViewSet(APITestCase):
    """
    Tests for the API endpoints for retrieving stadium constants
    """

    def get_url(self):
        return reverse("constants-stadia-list")

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
        An authenticated request should return the projects constants in a dictionary
        """
        url = self.get_url()
        client = get_authenticated_client()
        response = client.get(url)

        stadia = STADIA[:]
        stadia.remove(ISSUEMELDING)

        expected_response = {"constants": stadia}
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json(), expected_response)


class SettingsPlannerViewSet(APITestCase):
    """
    Tests for the API endpoints for retrieving planner settings
    """

    def get_url(self):
        return reverse("settings-planner-list")

    def test_unauthenticated_request(self):
        """
        An unauthenticated request should not be possible
        """

        url = self.get_url()
        client = get_unauthenticated_client()
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @override_config(PLANNER_SETTINGS='{"foo_settings": "foo"}')
    def test_settings(self):
        """
        Should return the PLANNER_SETTINGS value
        """
        url = self.get_url()
        client = get_authenticated_client()
        response = client.get(url)

        expected_response = {"foo_settings": "foo"}

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json(), expected_response)

    @override_config(PLANNER_SETTINGS="")
    def test_no_settings_saved(self):
        """
        Should return the default example planner settings if PLANNER_SETTINGS aren't set
        """
        url = self.get_url()
        client = get_authenticated_client()
        response = client.get(url)

        expected_response = EXAMPLE_PLANNER_SETTINGS
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json(), expected_response)
