# TODO: Tests for this
import logging
from typing import Dict, Iterable, List

import requests
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


def fetch_cases_data(
    ids: Iterable[str],
    auth_header=None,
    timeout: int = 60,
) -> Dict[str, dict]:
    """
    Batch fetch case details from Zaken and return a dict keyed by stringified id.

    - Uses /cases/data/?ids=... in a single request.
    - Accepts ids as strings or ints; keys in the result are strings.
    """
    unique_ids: List[str] = list({str(i) for i in ids if i is not None})
    if not unique_ids:
        return {}

    base_url = f"{settings.ZAKEN_API_URL}/cases/data/"
    headers = get_headers(auth_header)

    params = {
        "ids": ",".join(unique_ids),
        "page_size": len(unique_ids),
    }
    resp = requests.get(base_url, params=params, headers=headers, timeout=timeout)
    resp.raise_for_status()
    payload = resp.json()
    items = payload.get("results", payload)

    result: Dict[str, dict] = {}
    for item in items:
        # Zaken IDs are integers; TOP stores them as strings in Case.case_id
        result[str(item["id"])] = item

    return result
