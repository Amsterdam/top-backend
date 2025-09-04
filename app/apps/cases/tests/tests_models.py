"""
Tests for cases models
"""

from unittest.mock import Mock

from apps.cases.models import Case
from django.test import TestCase


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
        self.assertEquals(case.__str__(), CASE_ID)

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

        self.assertEquals(data, MOCK_DATA)
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
