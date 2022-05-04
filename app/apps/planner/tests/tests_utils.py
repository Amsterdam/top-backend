"""
Tests for the health views
"""
from apps.planner.utils import (
    filter_cases_with_postal_code,
    get_case_coordinates,
    remove_cases_from_list,
)
from django.test import TestCase
from settings.const import ISSUEMELDING

ONDERZOEK_BUITENDIENST = "Onderzoek buitendienst"
TWEEDE_CONTROLE = "2de Controle"


class UtilsTests(TestCase):
    def test_remove_cases_from_list(self):
        case_a = {"stadium": ONDERZOEK_BUITENDIENST, "id": "foo-a"}
        case_b = {"stadium": ISSUEMELDING, "id": "foo-b"}
        case_c = {"stadium": TWEEDE_CONTROLE, "id": "foo-c"}
        case_d = {"stadium": ONDERZOEK_BUITENDIENST, "id": "foo-d"}
        case_e = {"stadium": ISSUEMELDING, "id": "foo-e"}

        cases = [case_a, case_b, case_c, case_d, case_e]
        cases_to_remove = [case_b, case_e]

        result = remove_cases_from_list(cases, cases_to_remove)
        expected = [case_a, case_c, case_d]

        self.assertEquals(result, expected)

    def test_remove_cases_from_list_safety_fallback(self):
        """
        Wil still succeed if items from the cases_to_remove don't exist in the cases list
        """
        case_a = {"stadium": ONDERZOEK_BUITENDIENST, "id": "foo-a"}
        case_b = {"stadium": ISSUEMELDING, "id": "foo-b"}
        case_c = {"stadium": TWEEDE_CONTROLE, "id": "foo-c"}
        case_d = {"stadium": ONDERZOEK_BUITENDIENST, "id": "foo-d"}
        case_e = {"stadium": ISSUEMELDING, "id": "foo-e"}
        case_not_in_list = {"stadium": ISSUEMELDING, "id": "foo-f"}

        cases = [case_a, case_b, case_c, case_d, case_e]
        cases_to_remove = [case_a, case_b, case_not_in_list]

        result = remove_cases_from_list(cases, cases_to_remove)
        expected = [case_c, case_d, case_e]

        self.assertEquals(result, expected)

    def test_get_case_coordinates(self):
        case_a = {
            "address": {
                "lat": 0,
                "lng": 1,
            },
            "stadium": ONDERZOEK_BUITENDIENST,
            "id": "foo-a",
        }
        case_b = {
            "address": {"lat": 2, "lng": 3},
            "stadium": ISSUEMELDING,
            "id": "foo-b",
        }
        case_c = {
            "address": {"lat": 4, "lng": 5},
            "stadium": TWEEDE_CONTROLE,
            "id": "foo-c",
        }
        cases = [case_a, case_b, case_c]
        case_coordinates = get_case_coordinates(cases)
        expected = [[0, 1], [2, 3], [4, 5]]

        self.assertEquals(case_coordinates, expected)

    def test_filter_cases_with_postal_code_empty_list(self):
        """
        Should just return an empty list
        """
        FOO_CASE_A = {"postal_code": "1055XX"}
        cases = [FOO_CASE_A]
        filtered_cases = filter_cases_with_postal_code(cases, [])
        self.assertEqual(cases, filtered_cases)

    def test_filter_cases_with_postal_code_wrong_range(self):
        """
        Should throw error if the start range is larger than end range
        """
        FOO_START_RANGE = 2000
        FOO_END_RANGE = 1000
        FOO_CASE_A = {"postal_code": "1055XX"}
        cases = [FOO_CASE_A]

        RANGES = [{"range_start": FOO_START_RANGE, "range_end": FOO_END_RANGE}]

        with self.assertRaises(ValueError):
            filter_cases_with_postal_code(cases, RANGES)

    def test_filter_cases_with_postal_code(self):
        """
        Returns the cases which fall within the given range
        """
        FOO_START_RANGE = 1000
        FOO_END_RANGE = 2000
        RANGES = [{"range_start": FOO_START_RANGE, "range_end": FOO_END_RANGE}]

        FOO_CASE_A = {"address": {"postal_code": "1055XX"}}
        FOO_CASE_B = {"address": {"postal_code": "2055XX"}}
        FOO_CASE_C = {"address": {"postal_code": "2000XX"}}
        FOO_CASE_D = {"address": {"postal_code": "1000XX"}}
        FOO_CASE_E = {"address": {"postal_code": "0000XX"}}

        cases = [FOO_CASE_A, FOO_CASE_B, FOO_CASE_C, FOO_CASE_D, FOO_CASE_E]

        filtered_cases = filter_cases_with_postal_code(cases, RANGES)

        self.assertEquals(filtered_cases, [FOO_CASE_A, FOO_CASE_C, FOO_CASE_D])

    def test_filter_cases_with_multiple_postal_code_ranges(self):
        """
        Returns the cases which fall within the given range
        """
        RANGES = [
            {"range_start": 1055, "range_end": 1057},
            {"range_start": 2000, "range_end": 2050},
        ]

        FOO_CASE_A = {"address": {"postal_code": "1055XX"}}
        FOO_CASE_B = {"address": {"postal_code": "1056XX"}}
        FOO_CASE_C = {"address": {"postal_code": "1060XX"}}
        FOO_CASE_D = {"address": {"postal_code": "2000XX"}}
        FOO_CASE_E = {"address": {"postal_code": "2050XX"}}

        cases = [FOO_CASE_A, FOO_CASE_B, FOO_CASE_C, FOO_CASE_D, FOO_CASE_E]

        filtered_cases = filter_cases_with_postal_code(cases, RANGES)

        self.assertEquals(
            filtered_cases, [FOO_CASE_A, FOO_CASE_B, FOO_CASE_D, FOO_CASE_E]
        )
