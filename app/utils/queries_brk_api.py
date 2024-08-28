# TODO: Write tests for these functions
import logging
from datetime import datetime, timedelta

import requests
from constance.models import Constance
from django.conf import settings
from tenacity import after_log, retry, stop_after_attempt

logger = logging.getLogger(__name__)


def get_token():
    key = settings.CONSTANCE_BRK_AUTHENTICATION_TOKEN_KEY
    token, created = Constance.objects.get_or_create(key=key)
    return token.value


def get_expiry():
    key = settings.CONSTANCE_BRK_AUTHENTICATION_TOKEN_EXPIRY_KEY
    expiry, created = Constance.objects.get_or_create(key=key)
    expiry = expiry.value

    if not expiry == "":
        return expiry


def set_constance(key, value):
    constance_object, created = Constance.objects.get_or_create(key=key)
    constance_object.value = value
    constance_object.save()


def set_token(token):
    set_constance(settings.CONSTANCE_BRK_AUTHENTICATION_TOKEN_KEY, token)


def set_expiry(expiry):
    set_constance(settings.CONSTANCE_BRK_AUTHENTICATION_TOKEN_EXPIRY_KEY, expiry)


def request_new_token():
    logger.error("Start request_new_token")
    payload = {
        "grant_type": "client_credentials",
        "client_id": settings.BRK_ACCESS_CLIENT_ID,
        "client_secret": settings.BRK_ACCESS_CLIENT_SECRET,
    }

    token_request_url = settings.BRK_ACCESS_URL
    try:
        logger.error("token req url", token_request_url)
        logger.error("token req payload", payload)
        response = requests.post(token_request_url, data=payload, timeout=0.5)
    except Exception as e:
        logger.error("Request token error: ", e)
    response.raise_for_status()
    response_json = response.json()
    logger.error("RESPONSE JSON: ", response_json)
    access_token = response_json.get("access_token")
    logger.error("ACCESS TOKEN: ", access_token)
    set_token(access_token)

    expires_in = response_json.get("expires_in")
    expiry = datetime.now() + timedelta(seconds=expires_in)
    set_expiry(expiry)


def get_brk_request_headers():
    """
    Returns BRK request header for authenticated requests, with a valid bearer token
    """
    expiry = get_expiry()

    if expiry and type(expiry) is str:
        expiry = datetime.fromisoformat(expiry)

    if not expiry or expiry < datetime.now():
        request_new_token()

    token = get_token()

    if token is None or token == "":
        raise Exception("No authorization bearer token for BRK request")

    headers = {
        "Authorization": f"Bearer {token}",
        "content-type": "application/json",
    }

    return headers


@retry(stop=stop_after_attempt(3), after=after_log(logger, logging.ERROR))
def request_brk_data(bag_id):
    headers = get_brk_request_headers()
    logger.error("Headers", headers)
    try:
        brk_data_request = requests.get(
            settings.BRK_API_OBJECT_EXPAND_URL,
            params={"verblijfsobjecten__id": bag_id},
            headers=headers,
            timeout=0.5,
        )
    except Exception as e:
        logger.error("ERR: ", e)
    brk_data_request.raise_for_status()
    brk_data = brk_data_request.json()
    return brk_data


def get_brk_data(bag_id):
    """
    Does an authenticated request to BRK, and returns the owners of a given bag_id location
    """
    try:
        # Input validation
        if not bag_id:
            raise ValueError("No BAG ID given for BRK request")

        brk_data = request_brk_data(bag_id)
        return brk_data
    except Exception as e:
        logger.error("Requesting BRK data failed: {}".format(str(e)))
        error_objects = {
            "error": str(e),
            "bag_id": bag_id,
            "api_url": settings.BRK_API_OBJECT_EXPAND_URL,
        }
        return error_objects
