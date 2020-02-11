import requests
import logging
from datetime import datetime, timedelta
from constance.backends.database.models import Constance
from django.conf import settings

logger = logging.getLogger(__name__)

def get_token():
    key = settings.CONSTANCE_BRK_AUTHENTICATION_TOKEN_KEY
    token, created = Constance.objects.get_or_create(key=key)
    return token.value

def get_expiry():
    key = settings.CONSTANCE_BRK_AUTHENTICATION_TOKEN_EXPIRY_KEY
    expiry, created = Constance.objects.get_or_create(key=key)
    return expiry.value

def set_constance(key, value):
    constance_object, created = Constance.objects.get_or_create(key=key)
    constance_object.value = value
    constance_object.save()

def set_token(token):
    set_constance(
        settings.CONSTANCE_BRK_AUTHENTICATION_TOKEN_KEY,
        token
    )

def set_expiry(expiry):
    set_constance(
        settings.CONSTANCE_BRK_AUTHENTICATION_TOKEN_EXPIRY_KEY,
        expiry
    )

def request_new_token():
    payload = {
        'grant_type': 'client_credentials',
        'client_id': settings.BRK_ACCESS_CLIENT_ID,
        'client_secret': settings.BRK_ACCESS_CLIENT_SECRET,
    }

    try:
        token_request_url = settings.BRK_ACCESS_URL

        response = requests.post(token_request_url, data=payload)
        response.raise_for_status()
        response_json = response.json()

        access_token = response_json.get('access_token')
        set_token(access_token)

        expires_in = response_json.get('expires_in')
        expiry = datetime.now() + timedelta(seconds=expires_in)
        set_expiry(expiry)

    except Exception as e:
        logger.error('Requesting BRK access token failed: {}'.format(str(e)))
        return {'error': str(e)}
    return

def get_brk_request_headers():
    """
    Returns BRK request header for authenticated requests, with a valid bearer token
    """
    expiry = get_expiry()

    if expiry is None or expiry == '' or expiry < datetime.now():
        request_new_token()

    token = get_token()

    if token is None or token == '':
        raise Exception('No authorization bearer token for BRK request')

    headers = {
        'Authorization': "Bearer {}".format(token),
        'content-type': "application/json",
    }

    return headers


def get_brk_data(bag_id):
    '''
    Does an authenticated request to BRK, and returns the owners of a given bag_id location
    '''
    try:
        if not bag_id:
            raise Exception('No BAG ID given for BRK request')

        headers = get_brk_request_headers()
        brk_data_request = requests.get(
            settings.BRK_API_OBJECT_EXPAND_URL,
            params={'verblijfsobjecten__id': bag_id},
            headers=headers,
            timeout=1.5
        )

        brk_data_request.raise_for_status()
        brk_data = brk_data_request.json()
        brk_owners = brk_data.get(
            'results',
            timeout=1.5)[0].get('rechten')

        return {
            'owners': brk_owners
        }

    except Exception as e:
        logger.error('Requesting BRK data failed: {}'.format(str(e)))
        return {'error': str(e)}
