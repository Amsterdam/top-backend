# TODO: Tests for this
import logging

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


def get_fraudprediction_cases_from_AZA_by_model_name(model_name):
    from apps.cases.mock import get_zaken_case_list
    from apps.planner.models import TeamSettings

    team_settings = TeamSettings.objects.filter(
        enabled=True,
        fraud_prediction_model=model_name,
    ).first()

    if settings:
        if settings.USE_ZAKEN_MOCK_DATA:
            return get_zaken_case_list()
        else:
            logger.info("Get from AZA: state_types")
            state_types = settings.AZA_CASE_STATE_TYPES
            logger.info(state_types)

            logger.info("Get from AZA: cases")

            url = f"{settings.ZAKEN_API_URL}/cases/"

            queryParams = {
                "open_cases": "true",
                "state_types": [str(state.get("id", 0)) for state in state_types],
                "theme": (
                    team_settings.get("zaken_team_id")
                    if team_settings is not None
                    else None
                ),
                "page_size": 1000,
            }
            logger.info("With queryParams")
            logger.info(queryParams)
            response = requests.get(
                url,
                params=queryParams,
                timeout=60,
                headers=get_headers(),
            )
            response.raise_for_status()
            return response.json().get("results")
    return []
