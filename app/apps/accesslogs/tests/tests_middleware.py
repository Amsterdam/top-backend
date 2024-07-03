"""
Tests for accesslogs middleware
"""

from unittest.mock import Mock

from apps.accesslogs.middleware import LoggingMiddleware
from apps.accesslogs.models import LogEntry
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

FOO_URI = "FOO_URI"
FOO_META = "FOO_META"
FOO_REQUEST_METHOD = "GET"
FOO_USER_EMAIL = "foo@foo.com"
FOO_USER_ID = "FOO_USER_ID"

FOO_RESPONSE = "FOO Response"
FOO_RESPONSE_STATUS_CODE = "200"


def get_response_mock(request):
    response = Mock()
    response.response = FOO_RESPONSE
    response.status_code = FOO_RESPONSE_STATUS_CODE
    return response


REQUEST = Mock()
REQUEST.path = FOO_URI
REQUEST.META = FOO_META
REQUEST.method = FOO_REQUEST_METHOD
REQUEST.user = AnonymousUser()


class AccessLogsMiddlewareTest(TestCase):
    def test_returns_unaltered_response(self):
        """
        The accesslogs middleware passes and doesn't alter a response
        """
        logging_middleware = LoggingMiddleware(get_response_mock)
        response = logging_middleware(REQUEST)
        initial_response = get_response_mock("")

        self.assertEqual(response.response, initial_response.response)
        self.assertEqual(response.status_code, initial_response.status_code)

    def test_anonymous_log_creation(self):
        """
        The accesslogs middleware creates a LogEntry object for an anonymous request
        """
        self.assertEqual(LogEntry.objects.count(), 0)

        logging_middleware = LoggingMiddleware(get_response_mock)
        logging_middleware(REQUEST)

        self.assertEqual(LogEntry.objects.count(), 1)

    def test_user_log_creation(self):
        """
        The accesslogs middleware creates a log for an authenticated user request
        """
        self.assertEqual(LogEntry.objects.count(), 0)

        USER_REQUEST = Mock()
        USER_REQUEST.path = FOO_URI
        USER_REQUEST.META = FOO_META
        USER_REQUEST.method = FOO_REQUEST_METHOD
        USER_REQUEST.user = Mock()
        USER_REQUEST.user.email = FOO_USER_EMAIL
        USER_REQUEST.user.id = FOO_USER_ID

        logging_middleware = LoggingMiddleware(get_response_mock)
        logging_middleware(USER_REQUEST)

        log_entry = LogEntry.objects.all()[0]
        log_entry = LogEntry.objects.get(
            request_user_email=FOO_USER_EMAIL, request_user_id=FOO_USER_ID
        )
        self.assertIsNotNone(log_entry)

    def test_path_exemptions(self):
        """
        No access logs should be created if a request path is exempt
        """
        self.assertEqual(LogEntry.objects.count(), 0)

        with self.settings(ACCESS_LOG_EXEMPTIONS=(FOO_URI,)):
            logging_middleware = LoggingMiddleware(get_response_mock)
            logging_middleware(REQUEST)

        self.assertEqual(LogEntry.objects.count(), 0)
