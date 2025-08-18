"""
Tests for the health util functions
"""

import json
from unittest.mock import Mock, patch

from apps.health.utils import (
    assert_health_database_tables,
    assert_health_generic,
    assert_health_table,
    get_health_response,
    is_table_filled_query,
)
from django.test import TestCase

DATABASE_NAME = "foo-test-db"
TABLE_NAME = "foo-table"
SUCCESS_MESSAGE = {"message": "foo-success"}
ERROR_MESSAGE = "foo-error"


class GetHealthResponseTests(TestCase):
    def test_get_health_response_execute(self):
        """
        get_health_response executes the given function
        """
        health_check = Mock()
        get_health_response(health_check, SUCCESS_MESSAGE)
        health_check.assert_called()

    def test_get_health_response_success(self):
        """
        get_health_response should return a 200 status code if the given health_checks succeeds
        """
        health_check = Mock()
        response = get_health_response(health_check, SUCCESS_MESSAGE)
        self.assertEqual(response.status_code, 200)

    def test_get_health_response_success_message(self):
        """
        get_health_response should return the given success message if the health check succeeds
        """
        health_check = Mock()
        response = get_health_response(health_check, SUCCESS_MESSAGE)
        self.assertEqual(json.loads(response.content), SUCCESS_MESSAGE)

    def test_get_health_response_fail(self):
        """
        get_health_response should return a 500 status code if the given health_checks fails
        """
        health_check = Mock(side_effect=Exception(ERROR_MESSAGE))
        response = get_health_response(health_check, SUCCESS_MESSAGE)
        self.assertEqual(response.status_code, 500)

    def test_get_health_response_fail_message(self):
        """
        get_health_response should return a fail message if the health check fails
        """
        health_check = Mock(side_effect=Exception(ERROR_MESSAGE))
        response = get_health_response(health_check, SUCCESS_MESSAGE)
        self.assertEqual(json.loads(response.content), {"error": ERROR_MESSAGE})

    def test_is_table_filled_query(self):
        """
        is_table_filled_query should give query which counts the given table
        """
        FOO_TABLE_NAME = "foo-table"
        query = is_table_filled_query(FOO_TABLE_NAME)

        self.assertEqual(
            "SELECT reltuples::bigint FROM pg_catalog.pg_class WHERE relname ="
            " 'foo-table'",
            query,
        )


class TableFilledQueryTests(TestCase):
    def test_is_table_filled_query(self):
        """
        is_table_filled_query should give query which counts the given table
        """
        FOO_TABLE_NAME = "foo-table"
        query = is_table_filled_query(FOO_TABLE_NAME)

        self.assertEqual(
            "SELECT reltuples::bigint FROM pg_catalog.pg_class WHERE relname ="
            " 'foo-table'",
            query,
        )


class HealthTableTests(TestCase):
    @patch("apps.health.utils.connections")
    def test_assert_health_table_success(self, mock_connections):
        """
        assert_health_table executes successfully when the query count is more than 0
        """
        mock_connections[DATABASE_NAME] = Mock()
        mock_connections[DATABASE_NAME].cursor = Mock()
        cursor = mock_connections[DATABASE_NAME].cursor
        cursor.return_value = Mock()
        cursor.return_value.fetchone.return_value = (1, 0)

        assert_health_table(DATABASE_NAME, TABLE_NAME)

    @patch("apps.health.utils.connections")
    def test_assert_health_table_error(self, mock_connections):
        """
        assert_health_table raises an error when the query count is 0
        """
        mock_connections[DATABASE_NAME] = Mock()
        mock_connections[DATABASE_NAME].cursor = Mock()
        cursor = mock_connections[DATABASE_NAME].cursor
        cursor.return_value = Mock()
        cursor.return_value.fetchone.return_value = (0, 0)

        with self.assertRaises(Exception):
            assert_health_table(DATABASE_NAME, TABLE_NAME)

    @patch("apps.health.utils.connections")
    def test_assert_health_table_executes_query(self, mock_connections):
        """
        assert_health_table executes a query
        """
        mock_connections[DATABASE_NAME] = Mock()
        mock_connections[DATABASE_NAME].cursor = Mock()
        mock_connections[DATABASE_NAME].cursor.return_value = Mock()
        cursor = mock_connections[DATABASE_NAME].cursor
        cursor.return_value.fetchone.return_value = (1, 0)

        assert_health_table(DATABASE_NAME, TABLE_NAME)

        # Checks if the execute was called
        cursor.return_value.execute.assert_called()


class HealthTablesTests(TestCase):
    @patch("apps.health.utils.assert_health_table")
    def test_assert_health_tables(self, mock_assert_health_table):
        """
        assert_health_database_tables calls assert_health_table 1 times for number of tables
        """
        assert_health_database_tables(DATABASE_NAME, [TABLE_NAME])

        self.assertEqual(mock_assert_health_table.call_count, 1)

    @patch("apps.health.utils.assert_health_table")
    def test_assert_health_tables_2(self, mock_assert_health_table):
        """
        assert_health_database_tables calls assert_health_table n times for number of tables
        """
        assert_health_database_tables(DATABASE_NAME, [TABLE_NAME, TABLE_NAME])
        self.assertEqual(mock_assert_health_table.call_count, 2)

    @patch("apps.health.utils.assert_health_table")
    def test_assert_health_tables_arguments(self, mock_assert_health_table):
        """
        assert_health_database_tables calls assert_health_table with the correct database and table arguments
        """
        assert_health_database_tables(DATABASE_NAME, [TABLE_NAME])
        mock_assert_health_table.assert_called_with(DATABASE_NAME, TABLE_NAME)


class HealthGenericTests(TestCase):
    @patch("apps.health.utils.connections")
    def test_assert_health_generic_success(self, mock_connections):
        """
        assert_health_generic executes successfully
        """
        mock_connections[DATABASE_NAME] = Mock()
        assert_health_generic(DATABASE_NAME)

    @patch("apps.health.utils.connections")
    def test_assert_health_generic_error(self, mock_connections):
        """
        assert_health_generic raises an error when the query is unsuccessful
        """
        mock_connections[DATABASE_NAME] = Mock()
        mock_connections[DATABASE_NAME].cursor.return_value = Mock()
        mock_connections[DATABASE_NAME].cursor.return_value.fetchone = Mock(
            side_effect=Exception(ERROR_MESSAGE)
        )

        with self.assertRaises(Exception):
            assert_health_generic(DATABASE_NAME)
