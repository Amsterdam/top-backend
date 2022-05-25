import logging

import requests
from django.conf import settings
from tenacity import after_log, retry, stop_after_attempt

logger = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(3), after=after_log(logger, logging.ERROR))
def get_bag_id(case):
    street_name = case.get("street_name")
    street_number = case.get("street_number")

    suffix_letter = case.get("suffix_letter", "") or ""
    suffix = case.get("suffix", "") or ""

    query = "{} {} {}{}".format(street_name, street_number, suffix_letter, suffix)
    address_search = requests.get(
        settings.BAG_API_SEARCH_URL, params={"q": query}, timeout=0.5
    )

    return (
        address_search.json().get("results", [])[0].get("adresseerbaar_object_id", None)
    )


def get_bag_search_query(address):
    """
    Constructs a BAG search query using the address data
    """
    sttnaam = address.get("postal_code")
    hsnr = address.get("number")

    hsltr = address.get("suffix_letter", "") or ""
    toev = address.get("suffix", "") or ""

    query = "{} {} {}{}".format(sttnaam, hsnr, hsltr, toev)

    return query.strip()


@retry(stop=stop_after_attempt(3), after=after_log(logger, logging.ERROR))
def do_bag_search_address(address):
    """
    Search BAG using a address
    """
    query = get_bag_search_query(address)
    address_search = requests.get(
        settings.BAG_API_SEARCH_URL, params={"q": query}, timeout=0.5
    )
    return address_search.json()


@retry(stop=stop_after_attempt(3), after=after_log(logger, logging.ERROR))
def do_bag_search_id(address):
    """
    Search BAG using a AZA 'bag_id'
    """

    id = address.get("bag_id")
    address_search = requests.get(
        settings.BAG_API_SEARCH_URL, params={"q": id}, timeout=0.5
    )
    return address_search.json()


@retry(stop=stop_after_attempt(3), after=after_log(logger, logging.ERROR))
def get_address_bag_data(address_uri):
    address_bag_data = requests.get(address_uri, timeout=0.5)
    return address_bag_data.json()


def do_bag_search(address):
    """
    Search BAG. Uses a BAG id, or an address from AZA.
    """

    # First search using an addresss
    address_search = do_bag_search_address(address)

    # If that search didn't give any results, try using the Landelijk BAG id
    if address_search["count"] == 0:
        address_search = do_bag_search_id(address)

    return address_search


def get_bag_data_by_bag_id(address):
    try:
        address_search = do_bag_search(address)
        # Do a request using the the objects href
        address_uri = address_search["results"][0]["_links"]["self"]["href"]
        return get_address_bag_data(address_uri)

    except Exception as e:
        logger.error("Requesting BAG data failed: {}".format(str(e)))

        error_objects = {
            "error": str(e),
            "api_url": settings.BAG_API_SEARCH_URL,
            "address": address,
        }
        return error_objects
