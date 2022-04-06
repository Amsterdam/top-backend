import logging

from apps.fraudprediction.utils import get_fraud_prediction
from apps.planner.algorithm.base import ItineraryGenerateAlgorithm
from apps.planner.const import MAX_SUGGESTIONS_COUNT
from apps.planner.utils import calculate_geo_distances

LOGGER = logging.getLogger(__name__)


class ItineraryGenerateSuggestions(ItineraryGenerateAlgorithm):
    """Generates a list of suggestion based on a given location"""

    def generate(self, location):

        cases = self.__get_eligible_cases__()

        if not cases:
            LOGGER.warning("No eligible cases, could not generate suggestions")
            return []

        # Calculate a list of distances for each case
        center = (location.get("lat"), location.get("lng"))
        distances = calculate_geo_distances(center, cases)

        # Add the distances and fraud predictions to the cases
        for index, case in enumerate(cases):
            case["distance"] = distances[index]
            case["fraud_prediction"] = get_fraud_prediction(case.get("id"))

        # Sort the cases based on distance
        sorted_cases = sorted(cases, key=lambda item: item["distance"])[
            :MAX_SUGGESTIONS_COUNT
        ]
        return sorted_cases
