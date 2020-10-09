import logging

from apps.planner.utils import (
    filter_cases,
    filter_cases_with_missing_coordinates,
    filter_cases_with_postal_code,
    filter_out_cases,
    remove_cases_from_list,
)
from settings.const import STADIA
from utils.queries_planner import get_cases_from_bwv

LOGGER = logging.getLogger(__name__)


class ItineraryGenerateAlgorithm:
    """ An abstract class which forms the basis of itinerary generating algorithms """

    def __init__(self, settings, postal_code_settings=[]):
        self.opening_date = settings.opening_date
        self.stadia = STADIA
        self.target_length = int(settings.target_length)
        self.postal_code_ranges = [
            vars(postal_code_setting) for postal_code_setting in postal_code_settings
        ]

        try:
            self.primary_stadium = settings.primary_stadium.name
        except AttributeError:
            self.primary_stadium = None

        self.projects = [project.name for project in settings.projects.all()]
        self.secondary_stadia = [
            stadium.name for stadium in settings.secondary_stadia.all()
        ]
        self.exclude_stadia = [
            stadium.name for stadium in settings.exclude_stadia.all()
        ]
        self.exclude_cases = []

        try:
            self.start_case_id = settings.start_case.case_id
        except AttributeError:
            self.start_case_id = None

    def __get_filter_stadia__(self):
        """
        Gets a list of filter stadia to filter on
        """
        return STADIA

    def __get_eligible_cases__(self):
        """
        Returns a list of eligible cases using the settings object
        """
        cases = get_cases_from_bwv(self.opening_date, self.projects, self.stadia)
        LOGGER.info("Total list of cases: {}".format(len(cases)))

        filter_stadia = self.__get_filter_stadia__()

        LOGGER.info("Filter stadia: {}".format(str(filter_stadia)))
        LOGGER.info("Exclude stadia: {}".format(str(self.exclude_stadia)))
        LOGGER.info("Projects: {}".format(str(self.projects)))
        LOGGER.info("Opening date: {}".format(str(self.opening_date)))

        filtered_cases = filter_cases(cases, filter_stadia)
        LOGGER.info(
            "Total cases after filtering stadia: {}".format(len(filtered_cases))
        )

        filtered_cases = filter_out_cases(filtered_cases, self.exclude_stadia)
        LOGGER.info(
            "Total cases after excluding stadia: {}".format(len(filtered_cases))
        )

        filtered_cases = filter_cases_with_missing_coordinates(filtered_cases)
        LOGGER.info(
            "Total cases after filtering on missing coordinates: {}".format(
                len(filtered_cases)
            )
        )

        filtered_cases = filter_cases_with_postal_code(
            filtered_cases, self.postal_code_ranges
        )
        LOGGER.info(
            "Total cases after filtering on postal codes: {}".format(
                len(filtered_cases)
            )
        )

        exclude_cases = [{"case_id": case.case_id} for case in self.exclude_cases]
        filtered_cases = remove_cases_from_list(filtered_cases, exclude_cases)
        LOGGER.info(
            "Total cases after removing exclude cases: {}".format(len(filtered_cases))
        )

        if not filtered_cases:
            LOGGER.warning("No eligible cases found")
            return []

        return filtered_cases

    def exclude(self, cases):
        """
        Makes sure the givens are not used when generating a list
        """
        self.exclude_cases = cases

    def generate(self):
        raise NotImplementedError()
