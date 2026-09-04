"""
Tests for cases models
"""

from datetime import date, timedelta
from unittest.mock import Mock

from apps.cases.models import Case
from apps.itinerary.models import Itinerary, ItineraryItem, ItineraryTeamMember
from apps.users.models import User
from django.test import TestCase
from freezegun import freeze_time


class CaseModelTest(TestCase):
    def test_create_case_object(self):
        """
        A Case object can be created
        """
        self.assertEqual(Case.objects.count(), 0)
        Case.objects.create(case_id="FOO")
        self.assertEqual(Case.objects.count(), 1)

    def test_case_object_string(self):
        """
        A Case oject's string representation is the same as it's case_id
        """
        CASE_ID = "CASE ID FOO"
        case = Case.objects.create(case_id=CASE_ID)
        self.assertEqual(case.__str__(), CASE_ID)

    def test_case_object_data(self):
        """
        The data property calls get_case util function using the Case object's ID
        """
        CASE_ID = "CASE ID FOO"
        case = Case.objects.create(case_id=CASE_ID)

        # This patches the objects __get_case__ function
        MOCK_DATA = "FOO"
        case.__get_case__ = Mock()
        case.__get_case__.return_value = MOCK_DATA

        data = case.data

        self.assertEqual(data, MOCK_DATA)
        case.__get_case__.assert_called_with(CASE_ID)

    def test_case_get_function(self):
        """
        The Case get function is a wrapper for get_or_create, and simplifies Case creation
        """
        FOO_ID = "FOO_ID"

        self.assertEqual(Case.objects.count(), 0)
        Case.get(FOO_ID)
        self.assertEqual(Case.objects.count(), 1)

        # Another get will nog create another object
        Case.get(FOO_ID)
        self.assertEqual(Case.objects.count(), 1)

    def test_get_location(self):
        """
        Should return the case geolocation data
        """
        case = Case.get("FOO")

        # This patches the objects __get_case__ function
        MOCK_DATA = {"address": {"lat": 0, "lng": 1, "foo": "OTHER DATA"}}
        case.__get_case__ = Mock()
        case.__get_case__.return_value = MOCK_DATA

        location = case.get_location()

        self.assertEqual(location, {"lat": 0, "lng": 1})


class CaseGetTeamsTest(TestCase):
    """
    Tests for Case.get_teams, which returns the teams (per itinerary) that are
    scheduled to visit a case. Only itineraries of today or in the future count.
    """

    def _make_itinerary(self, created_at):
        # created_at uses auto_now_add, so freeze time to control it
        with freeze_time(created_at):
            return Itinerary.objects.create()

    def _add_case_to_itinerary(self, itinerary, case, email):
        ItineraryItem.objects.create(itinerary=itinerary, case=case)
        user = User.objects.create(email=email)
        ItineraryTeamMember.objects.create(itinerary=itinerary, user=user)

    def test_no_itineraries_returns_empty_list(self):
        case = Case.objects.create(case_id="FOO")
        self.assertEqual(case.get_teams(), [])

    def test_returns_team_members_for_todays_itinerary(self):
        case = Case.objects.create(case_id="FOO")
        itinerary = self._make_itinerary(date.today())
        self._add_case_to_itinerary(itinerary, case, "today@example.com")

        teams = case.get_teams()

        self.assertEqual(len(teams), 1)
        self.assertEqual(len(teams[0]), 1)
        self.assertEqual(teams[0][0]["user"]["email"], "today@example.com")

    def test_includes_future_itineraries(self):
        case = Case.objects.create(case_id="FOO")
        itinerary = self._make_itinerary(date.today() + timedelta(days=3))
        self._add_case_to_itinerary(itinerary, case, "future@example.com")

        self.assertEqual(len(case.get_teams()), 1)

    def test_excludes_past_itineraries(self):
        case = Case.objects.create(case_id="FOO")
        itinerary = self._make_itinerary(date.today() - timedelta(days=1))
        self._add_case_to_itinerary(itinerary, case, "past@example.com")

        self.assertEqual(case.get_teams(), [])

    def test_excludes_itineraries_without_this_case(self):
        case = Case.objects.create(case_id="FOO")
        other_case = Case.objects.create(case_id="BAR")
        itinerary = self._make_itinerary(date.today())
        self._add_case_to_itinerary(itinerary, other_case, "other@example.com")

        self.assertEqual(case.get_teams(), [])
