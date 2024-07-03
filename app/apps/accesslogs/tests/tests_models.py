"""
Tests for accesslogs models
"""

from apps.accesslogs.models import LogEntry
from django.db.utils import DataError
from django.test import TestCase

FOO_URI = "FOO_URI"
FOO_META = "FOO_META"
FOO_REQUEST_METHOD = "GET"
FOO_REQUEST_STATUS_CODE = "200"
FOO_USER_EMAIL = "foo@foo.com"
FOO_USER_ID = "FOO_USER_ID"


class AccessLogsModelTest(TestCase):
    def test_create_anonymous_log(self):
        """
        Create an anonymous log entry
        """
        self.assertEqual(LogEntry.objects.count(), 0)

        LogEntry.objects.create(
            request_uri=FOO_URI,
            request_meta=FOO_META,
            request_method=FOO_REQUEST_METHOD,
            response_status_code=FOO_REQUEST_STATUS_CODE,
        )

        self.assertEqual(LogEntry.objects.count(), 1)

    def test_create_user_log(self):
        """
        Create a log entry that is coupled to a user
        """
        self.assertEqual(LogEntry.objects.count(), 0)

        LogEntry.objects.create(
            request_user_email=FOO_USER_EMAIL,
            request_user_id=FOO_USER_ID,
            request_uri=FOO_URI,
            request_meta=FOO_META,
            request_method=FOO_REQUEST_METHOD,
            response_status_code=FOO_REQUEST_STATUS_CODE,
        )

        self.assertEqual(LogEntry.objects.count(), 1)

    def test_no_edit_logs(self):
        """
        A log cannot be edited once it's saved
        """

        log_entry = LogEntry.objects.create(
            request_uri=FOO_URI,
            request_meta=FOO_META,
            request_method=FOO_REQUEST_METHOD,
            response_status_code=FOO_REQUEST_STATUS_CODE,
        )

        log_entry.request_meta = "EDIT"

        with self.assertRaises(Exception):
            log_entry.save()

    def test_status_code_length(self):
        """
        A log status code cannot be longer than 3 characters
        """
        with self.assertRaises(DataError):
            LogEntry.objects.create(
                request_uri=FOO_URI,
                request_meta=FOO_META,
                request_method=FOO_REQUEST_METHOD,
                response_status_code="LONG_STATUS_CODE",
            )

    def test_date_created(self):
        """
        The date_created should be added automatically
        """

        log_entry = LogEntry.objects.create(
            request_uri=FOO_URI,
            request_meta=FOO_META,
            request_method=FOO_REQUEST_METHOD,
            response_status_code=FOO_REQUEST_STATUS_CODE,
        )

        self.assertIsNotNone(log_entry.created_at)
