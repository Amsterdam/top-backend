import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def fetch_bag_data_by_nummeraanduiding_id(nummeraanduiding_id):
    """
    Fetch BAG BENKAGG data using a nummeraanduiding_id.
    """
    url = f"{settings.BAG_BENKAGG_API_URL}{nummeraanduiding_id}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        return response.json()
    except Exception as exc:
        logger.error(f"Unexpected error during BAG API call: {exc}")
        raise


def get_bag_data_by_nummeraanduiding_id(nummeraanduiding_id):
    """
    Retrieve BAG BENKAGG data for a given nummeraanduiding_id.
    Logs and returns error details in case of failure.
    """
    try:
        bag_data = fetch_bag_data_by_nummeraanduiding_id(nummeraanduiding_id)
        return bag_data
    except Exception as error:
        logger.error(f"Failed to fetch BAG data: {error}")
        error_objects = {
            "error": str(error),
            "api_url": f"{settings.BAG_BENKAGG_API_URL}{nummeraanduiding_id}",
            "address": nummeraanduiding_id,
        }
        return error_objects
