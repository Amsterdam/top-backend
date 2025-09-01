# TODO: Tests for this
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def get_headers(auth_header=None):
    token = settings.SECRET_KEY_TOP_ZAKEN
    headers = {
        "Authorization": f"{auth_header}" if auth_header else f"{token}",
        "content-type": "application/json",
    }
    return headers


def date_to_string(date):
    if date:
        return str(date)

    return None


def assert_allow_push():
    assert settings.ZAKEN_API_URL, "ZAKEN_API_URL is not configured in settings."
    assert settings.PUSH_ZAKEN, "Pushes disabled"
