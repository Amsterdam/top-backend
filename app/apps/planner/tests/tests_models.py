import datetime

from apps.planner.models import DaySettings, TeamSettings
from django.test import TestCase
from model_bakery import baker


class CasesQueryParamsTest(TestCase):
    def test_team_settings_excludes_cases_with_open_sensitive_case_on_address(self):
        team_settings = baker.make(TeamSettings)

        params = team_settings.get_cases_query_params()

        self.assertEqual(params["has_open_sensitive_case_on_address"], "false")

    def test_day_settings_excludes_cases_with_open_sensitive_case_on_address(self):
        day_settings = baker.make(DaySettings, opening_date=datetime.date(2026, 1, 1))

        params = day_settings.get_cases_query_params()

        self.assertEqual(params["has_open_sensitive_case_on_address"], "false")

    def test_day_settings_include_is_bed_and_breakfast_when_configured(self):
        day_settings = baker.make(
            DaySettings,
            opening_date=datetime.date(2026, 1, 1),
            is_bed_and_breakfast=True,
        )

        params = day_settings.get_cases_query_params()

        self.assertTrue(params["is_bed_and_breakfast"])
