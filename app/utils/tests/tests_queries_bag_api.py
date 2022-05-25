"""
Tests for BAG queries
"""
from unittest.mock import Mock, patch

from django.conf import settings
from django.test import TestCase
from utils.queries_bag_api import (
    do_bag_search,
    do_bag_search_address,
    do_bag_search_id,
    get_bag_search_query,
)


class GetBagSearchQueryTest(TestCase):
    def test_get_search_query_basic(self):
        """
        Returns a search query given a postal code and a house number
        """
        address = {
            "postal_code": "postcode_foo",
            "number": "hsnr_foo",
        }

        result = get_bag_search_query(address)

        self.assertEquals(result, "postcode_foo hsnr_foo")

    def test_get_search_query_letter(self):
        """
        Returns a search query given a postal code, a house number, and a letter
        """
        address = {
            "postal_code": "postcode_foo",
            "number": "hsnr_foo",
            "suffix_letter": "hsltr_foo",
        }

        result = get_bag_search_query(address)

        self.assertEquals(result, "postcode_foo hsnr_foo hsltr_foo")

    def test_get_search_query_addition(self):
        """
        Returns a search query given a postal code, a house number, and an addition
        """
        address = {
            "postal_code": "postcode_foo",
            "number": "hsnr_foo",
            "suffix": "toev_foo",
        }

        result = get_bag_search_query(address)

        self.assertEquals(result, "postcode_foo hsnr_foo toev_foo")

    def test_get_search_query_all(self):
        """
        Returns a search query given all optional parameters
        """
        address = {
            "postal_code": "postcode_foo",
            "number": "hsnr_foo",
            "suffix_letter": "hsltr_foo",
            "suffix": "toev_foo",
        }

        result = get_bag_search_query(address)

        self.assertEquals(result, "postcode_foo hsnr_foo hsltr_footoev_foo")

    def test_get_search_query_none_hsltr(self):
        """
        Returns a clean search query with house number set to None
        """
        address = {
            "postal_code": "postcode_foo",
            "number": "hsnr_foo",
            "suffix_letter": None,
            "suffix": "toev_foo",
        }

        result = get_bag_search_query(address)

        self.assertEquals(result, "postcode_foo hsnr_foo toev_foo")

    def test_get_search_query_none_toev(self):
        """
        Returns a clean search query with house number set to None
        """
        address = {
            "postal_code": "postcode_foo",
            "number": "hsnr_foo",
            "suffix_letter": "hsltr_foo",
            "suffix": None,
        }

        result = get_bag_search_query(address)

        self.assertEquals(result, "postcode_foo hsnr_foo hsltr_foo")


class DoBagSearchAddressTest(TestCase):
    @patch("utils.queries_bag_api.get_bag_search_query")
    @patch("requests.get")
    def test_do_bag_search_address(self, mock_requests_get, mock_get_bag_search_query):
        """
        Does a get request to the BAG API using an address search query
        """

        address = "Foo"
        mock_get_bag_search_query.return_value = "Foo Query"

        do_bag_search_address(address)

        # The BAG search query is retrieved
        mock_get_bag_search_query.assert_called()

        # The GET request is performed
        mock_requests_get.assert_called_with(
            settings.BAG_API_SEARCH_URL, params={"q": "Foo Query"}, timeout=0.5
        )


class DoBagSearchIdTest(TestCase):
    @patch("requests.get")
    def test_do_bag_search_id(self, mock_requests_get):
        """
        Does a get request to the BAG API using a BAG ID
        """

        address = {"bag_id": "Foo ID"}

        do_bag_search_id(address)

        # The GET request is performed
        mock_requests_get.assert_called_with(
            settings.BAG_API_SEARCH_URL, params={"q": "Foo ID"}, timeout=0.5
        )


class DoBagSearchTest(TestCase):
    @patch("utils.queries_bag_api.do_bag_search_address")
    def test_do_bag_search(self, mock_do_bag_search):
        """
        Does a regular bag search using the address and returns the address search results
        """

        REGULAR_BAG_SEARCH_RESULT = {"count": 1, "results": ["Foo Result"]}
        MOCK_ADDRRESS = Mock()

        mock_do_bag_search.return_value = REGULAR_BAG_SEARCH_RESULT

        result = do_bag_search(MOCK_ADDRRESS)

        self.assertEquals(REGULAR_BAG_SEARCH_RESULT, result)

    @patch("utils.queries_bag_api.do_bag_search_id")
    @patch("utils.queries_bag_api.do_bag_search_address")
    def test_do_bag_search_fallback(self, mock_do_bag_search, mock_do_bag_search_id):
        """
        Does a BAG search using an ID as fallback when the regular search fails
        """
        # Regular search returns 0 results
        REGULAR_BAG_SEARCH_RESULT = {"count": 0, "results": []}

        mock_do_bag_search.return_value = REGULAR_BAG_SEARCH_RESULT

        ID_BAG_SEARCH_RESULT = "MOCK_BACK_SEARCH_ID Result"
        mock_do_bag_search_id.return_value = ID_BAG_SEARCH_RESULT

        MOCK_ADDRRESS = Mock()
        result = do_bag_search(MOCK_ADDRRESS)

        # As a result, the ID bag search results should be returned/used
        self.assertEquals(ID_BAG_SEARCH_RESULT, result)
