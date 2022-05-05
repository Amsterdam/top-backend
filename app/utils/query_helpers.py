import logging

from django.conf import settings
from django.db import connections

logger = logging.getLogger(__name__)


def query_to_list(cursor):
    columns = [col[0] for col in cursor.description]

    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def __get_bwv_cursor__():
    return connections[settings.BWV_DATABASE_NAME].cursor()


def do_query(query, args=None):
    try:
        cursor = __get_bwv_cursor__()
        cursor.execute(query, args)
        return query_to_list(cursor)

    except Exception as e:
        logger.error("BWV Database Query failed: {} {}".format(str(e), query))
        return []
