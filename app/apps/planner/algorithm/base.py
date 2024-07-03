import datetime
import logging

import requests
from apps.cases.mock import get_zaken_case_list
from apps.planner.utils import (
    get_cases_with_odd_or_even_ids,
    is_day_of_this_year_odd,
    remove_cases_from_list,
)
from django.conf import settings
from utils.queries_zaken_api import get_headers

logger = logging.getLogger(__name__)


class ItineraryGenerateAlgorithm:
    """An abstract class which forms the basis of itinerary generating algorithms"""

    def __init__(self, settings, postal_code_settings=[], **kwargs):
        self.auth_header = kwargs.get("auth_header")
        self.settings = settings
        self.opening_date = settings.opening_date
        self.target_length = int(settings.target_length)
        self.postal_code_ranges = [
            vars(postal_code_setting) for postal_code_setting in postal_code_settings
        ]
        self.settings.postal_code_ranges = self.postal_code_ranges

        try:
            self.start_case_id = settings.start_case.case_id
        except AttributeError:
            self.start_case_id = None

    def __get_eligible_cases__(self):
        logger.info("v2 __get_eligible_cases__")
        if settings.USE_ZAKEN_MOCK_DATA:
            cases = get_zaken_case_list()
        else:
            logger.info("Get from AZA: cases")

            url = f"{settings.ZAKEN_API_URL}/cases/"

            queryParams = self.settings.get_cases_query_params()
            logger.info("With queryParams")
            logger.info(queryParams)
            now = datetime.datetime.now()
            response = requests.get(
                url,
                params=queryParams,
                timeout=60,
                headers=get_headers(self.auth_header),
            )
            response.raise_for_status()
            logger.info("Request duration")
            logger.info(datetime.datetime.now() - now)

            cases = response.json().get("results")

        logger.info("initial case count")
        logger.info(len(cases))

        exclude_cases = [{"id": case.case_id} for case in self.exclude_cases]
        cases = remove_cases_from_list(cases, exclude_cases)
        logger.info("after remove_cases_from_list")
        logger.info(len(cases))

        if self.settings.day_settings.team_settings.fraudprediction_pilot_enabled:
            cases = get_cases_with_odd_or_even_ids(cases, odd=is_day_of_this_year_odd())
            logger.info("after get_cases_with_odd_or_even_ids")

        return cases

    def exclude(self, cases):
        """
        Makes sure the givens are not used when generating a list
        """
        self.exclude_cases = cases

    def generate(self):
        raise NotImplementedError()

    def sort_cases_by_distance(self, cases):
        return sorted(cases, key=lambda k: k.get("distance"))
