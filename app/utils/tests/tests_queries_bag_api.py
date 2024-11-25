"""
Tests for BAG queries
"""

from unittest.mock import Mock, patch

from django.conf import settings
from django.test import TestCase
from utils.queries_bag_api import (
    fetch_bag_data_by_nummeraanduiding_id,
    get_bag_data_by_nummeraanduiding_id,
)


class FetchBagDataByNummeraanduidingIdTest(TestCase):
    @patch("requests.get")
    def test_fetch_bag_data_by_nummeraanduiding_id_success(self, mock_requests_get):
        """
        Tests fetching BAG data successfully
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "some_data"}
        mock_requests_get.return_value = mock_response

        result = fetch_bag_data_by_nummeraanduiding_id("123456789")

        self.assertEqual(result, {"data": "some_data"})
        mock_requests_get.assert_called_once_with(
            f"{settings.BAG_BENKAGG_API_URL}123456789", timeout=0.5
        )

    @patch("requests.get")
    def test_fetch_bag_data_by_nummeraanduiding_id_failure(self, mock_requests_get):
        """
        Tests failure when the API returns an error or timeout
        """
        mock_requests_get.side_effect = Exception("API error")

        with self.assertRaises(Exception):
            fetch_bag_data_by_nummeraanduiding_id("123456789")


class GetBagDataByNummeraanduidingIdTest(TestCase):
    @patch("utils.queries_bag_api.fetch_bag_data_by_nummeraanduiding_id")
    def test_get_bag_data_by_nummeraanduiding_id_success(self, mock_fetch_bag_data):
        """
        Tests retrieving BAG data successfully
        """
        mock_fetch_bag_data.return_value = {"data": "some_data"}

        result = get_bag_data_by_nummeraanduiding_id("123456789")

        self.assertEqual(result, {"data": "some_data"})
        mock_fetch_bag_data.assert_called_once_with("123456789")

    @patch("utils.queries_bag_api.fetch_bag_data_by_nummeraanduiding_id")
    def test_get_bag_data_by_nummeraanduiding_id_failure(self, mock_fetch_bag_data):
        """
        Tests failure in fetching BAG data
        """
        mock_fetch_bag_data.side_effect = Exception("API error")

        result = get_bag_data_by_nummeraanduiding_id("123456789")

        expected_error = {
            "error": "API error",
            "api_url": f"{settings.BAG_BENKAGG_API_URL}123456789",
            "address": "123456789",
        }
        self.assertEqual(result, expected_error)
