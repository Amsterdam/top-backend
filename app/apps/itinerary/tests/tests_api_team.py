from apps.itinerary.models import Itinerary
from apps.users.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.utils.unittest_helpers import (
    get_authenticated_client,
    get_unauthenticated_client,
)


class ItineraryTeamsViewsTest(APITestCase):
    """
    Tests for the API endpoint for retrieving teams
    """

    def test_unauthenticated_request_get(self):
        """
        An unauthenticated request should not be possible
        """

        itinerary = Itinerary.objects.create()
        url = reverse("v1:itinerary-team", kwargs={"pk": itinerary.id})
        client = get_unauthenticated_client()
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_itinerary_without_team(self):
        """
        Should return an empty response if no team is associated to itinerary
        """
        itinerary = Itinerary.objects.create()
        url = reverse("v1:itinerary-team", kwargs={"pk": itinerary.id})
        client = get_authenticated_client()
        response = client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["team_members"], [])

    def test_itinerary_with_team(self):
        """
        Should return a list of user objects
        """
        itinerary = Itinerary.objects.create()
        user_a = User.objects.create(email="foo_a@foo.com")
        user_b = User.objects.create(email="foo_b@foo.com")
        itinerary.add_team_members([user_a.id, user_b.id])

        url = reverse("v1:itinerary-team", kwargs={"pk": itinerary.id})
        client = get_authenticated_client()
        response = client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_team_members = response.json()["team_members"]

        self.assertEqual(len(response_team_members), 2)
        self.assertEqual(response_team_members[0]["user"]["email"], user_a.email)
        self.assertEqual(response_team_members[1]["user"]["email"], user_b.email)

    def test_itinerary_add_team(self):
        """
        Adds a team to an itinerary through the API
        """
        itinerary = Itinerary.objects.create()
        user_a = User.objects.create(email="foo_a@foo.com")
        user_b = User.objects.create(email="foo_b@foo.com")

        self.assertEquals([], list(itinerary.team_members.all()))

        url = reverse("v1:itinerary-team", kwargs={"pk": itinerary.id})
        client = get_authenticated_client()

        data = {
            "team_members": [
                {"user": {"id": user_a.id}},
                {"user": {"id": user_b.id}},
            ]
        }
        response = client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        team_members = [
            team_member.user for team_member in itinerary.team_members.all()
        ]
        self.assertEquals([user_a, user_b], team_members)

    def test_itinerary_update_team(self):
        """
        Upate a team to an itinerary through the API
        """
        itinerary = Itinerary.objects.create()
        user_a = User.objects.create(email="foo_a@foo.com")
        user_b = User.objects.create(email="foo_b@foo.com")
        itinerary.add_team_members([user_b.id])

        url = reverse("v1:itinerary-team", kwargs={"pk": itinerary.id})
        client = get_authenticated_client()

        data = {
            "team_members": [
                {"user": {"id": user_a.id}},
                {"user": {"id": user_b.id}},
            ]
        }
        response = client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        team_members = [
            team_member.user for team_member in itinerary.team_members.all()
        ]
        self.assertEquals([user_a, user_b], team_members)
