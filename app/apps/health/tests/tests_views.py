"""
Tests for the health views
"""

from unittest.mock import Mock, patch

from apps.health.views import health_default
from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from app.utils.unittest_helpers import get_unauthenticated_client


class HealthViewsTests(TestCase):
    @patch("apps.health.views.assert_health_generic")
    def test_health_default(self, mock_assert_health_generic):
        """
        health_default calls assert_health_generic with the correct database
        """
        mock_request = Mock()
        health_default(mock_request)
        mock_assert_health_generic.assert_called_with(
            database_name=settings.DEFAULT_DATABASE_NAME
        )


class HealthViewsUrlsTests(TestCase):
    @patch("apps.health.views.assert_health_generic")
    def test_health_default_url_view(self, mock_assert_health_generic):
        """
        URL endpoint for health_default can be called
        """
        url = reverse("health-default")
        client = get_unauthenticated_client()
        response = client.get(url)

        mock_assert_health_generic.assert_called()
        self.assertEquals(response.status_code, 200)
