"""
Tests for helpers
"""

from datetime import datetime

from django.test import TestCase
from freezegun import freeze_time
from utils.date_helpers import get_days_in_range


@freeze_time("2019-12-25")
class GetDaysInRangeTest(TestCase):
    def test_no_days_in_range(self):
        """
        When start date and end date are equal, days should be 0
        """
        start_date = datetime(2019, 12, 25)
        end_date = start_date
        days_in_range = get_days_in_range(start_date, end_date)

        self.assertEqual(days_in_range, 0)

    def test_days_in_range(self):
        """
        Returns correct days in range
        """
        range_days = 3

        start_date = datetime(2019, 12, 25)
        end_date = start_date.replace(day=start_date.day + range_days)

        days_in_range = get_days_in_range(start_date, end_date)

        self.assertEqual(days_in_range, range_days)

    def test_error_for_incorrect_dates(self):
        """
        An error is thrown if the end date is earlier than the start date
        """
        with self.assertRaises(ValueError):
            start_date = datetime.now()
            end_date = start_date.replace(day=start_date.day - 1)
            get_days_in_range(start_date, end_date)

    def test_count_start_date_current_year(self):
        """
        Only count the days in the current year when start date falls in the current year
        """
        start_date = datetime(2019, 12, 30)
        end_date = datetime(2020, 2, 5)

        days = get_days_in_range(start_date, end_date)
        self.assertEqual(days, 2)

    # We set the current time specifically for this test case
    @freeze_time("2020-1-25")
    def test_count_end_date_current_year(self):
        """
        Only count the days in the current year when end date falls in the current year
        """
        start_date = datetime(2019, 12, 25)
        end_date = datetime(2020, 1, 5)

        days = get_days_in_range(start_date, end_date)
        self.assertEqual(days, 4)
