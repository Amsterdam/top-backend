from django.db import connections
from django.http import JsonResponse


def get_health_response(health_checks, success_dictionary):
    """
    Executes the given health_checks function,
    and returns a response based on the function's success
    """
    try:
        health_checks()
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse(success_dictionary, status=200)


def is_table_filled_query(table):
    """
    A fast query to check if a table is filled (with at least one entry)
    """
    return (
        "SELECT reltuples::bigint FROM pg_catalog.pg_class WHERE relname = '{}'".format(
            table
        )
    )


def assert_health_table(database_name, table):
    """
    Given a database and one table, checks if the table is filled with at least on entry
    """
    cursor = connections[database_name].cursor()
    query = is_table_filled_query(table)
    cursor.execute(query)
    row = cursor.fetchone()
    assert row, "The {} table in the {} database does not exist".format(
        table, database_name
    )
    assert row[0] > 0, "The {} table in the {} database is empty".format(
        table, database_name
    )


def assert_health_database_tables(database_name, tables):
    """
    Given a database and it's tables, this checks if all tables are filled
    """
    errors = []

    for table in tables:
        try:
            assert_health_table(database_name, table)
        except Exception as e:
            errors.append(str(e))

    if len(errors):
        raise Exception("".join(errors))


def assert_health_generic(database_name):
    """
    A basic check to see if a connection with the given database can be made
    """
    cursor = connections[database_name].cursor()
    cursor.execute("select 1")
    assert cursor.fetchone()
