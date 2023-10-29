import logging
import multiprocessing

from apps.cases.models import Case
from apps.fraudprediction.utils import get_fraud_predictions
from apps.planner.algorithm.base import ItineraryGenerateAlgorithm
from apps.planner.const import MAX_SUGGESTIONS_COUNT
from apps.planner.models import Weights
from apps.planner.utils import (
    calculate_geo_distances,
    is_day_of_this_year_odd,
    remove_cases_from_list,
)
from django.conf import settings
from joblib import Parallel, delayed

logger = logging.getLogger(__name__)


class ItineraryKnapsackSuggestions(ItineraryGenerateAlgorithm):
    def __init__(
        self, settings, postal_code_settings=[], settings_weights=None, **kwargs
    ):
        super().__init__(settings, postal_code_settings, **kwargs)

        self.weights = Weights()

        if settings_weights:
            self.weights = Weights(
                distance=settings_weights.distance,
                fraud_probability=settings_weights.fraud_probability,
                priority=settings_weights.priority,
            )

    def get_score(self, case):
        """
        Gets the score of the given case
        """
        distance = case.get("normalized_inverse_distance", 0)

        fraud_probability = case.get("fraud_prediction", {}).get("fraud_probability", 0)
        if (
            self.settings.day_settings.team_settings.fraudprediction_pilot_enabled
            and is_day_of_this_year_odd()
        ):
            fraud_probability = 0

        priority = (
            next(iter(case.get("schedules", [])), {"priority": {"weight": 0}})
            .get("priority", {})
            .get("weight", 0)
        )

        score = self.weights.score(
            distance,
            fraud_probability,
            priority,
        )

        return score

    def get_center(self, case):
        return case.get("address", {}).get("lat"), case.get("address", {}).get("lng")

    def generate(self, center_case, cases=[], fraud_predictions=[]):
        if not cases:
            cases = self.__get_eligible_cases__()

        if not cases:
            return []

        if not fraud_predictions:
            fraud_predictions = get_fraud_predictions()

        # Calculate a list of distances for each case
        center = self.get_center(center_case)
        distances = calculate_geo_distances(center, cases)
        max_distance = max(distances)

        # Add the distances and fraud predictions to the cases
        for index, case in enumerate(cases):
            case_id = str(case.get("id"))
            case["distance"] = distances[index]
            case["normalized_inverse_distance"] = (
                (max_distance - case["distance"]) / max_distance if max_distance else 0
            )
            case["fraud_prediction"] = fraud_predictions.get(case_id, {})
            case["score"] = self.get_score(case)

        # Sort the cases based on score
        sorted_cases = sorted(cases, key=lambda case: case["score"], reverse=True)

        return sorted_cases[:MAX_SUGGESTIONS_COUNT]


class ItineraryKnapsackList(ItineraryKnapsackSuggestions):
    def get_best_list(self, candidates):
        best_list = max(candidates, key=lambda candidate: candidate.get("score"))
        return best_list["list"]

    def is_same_address(self, case_a, case_b):
        same_street = case_a.get("address", {}).get("street_name") == case_b.get(
            "address", {}
        ).get("street_name")
        same_number = case_a.get("address", {}).get("number") == case_b.get(
            "address", {}
        ).get("number")
        return same_street and same_number

    def shorten_list(self, cases_all):
        cases_all = cases_all.copy()
        cases_all.reverse()
        cases = []

        counter = self.target_length

        while counter > 0 and len(cases_all):
            case = cases_all.pop()
            cases.append(case)
            counter -= 1

            if len(cases_all):
                next_case = cases_all[-1]

                if self.is_same_address(case, next_case):
                    counter += 1

        return cases

    def parallelized_function(self, case, cases, fraud_predictions, index):
        suggestions = super().generate(case, cases, fraud_predictions)
        cases = self.shorten_list(suggestions)

        score = sum([case["score"] for case in cases])
        return {"score": score, "list": cases}

    def generate(self, auth_header=None):
        fraud_predictions = get_fraud_predictions()
        if self.start_case_id:
            case = Case.get(
                case_id=self.start_case_id,
            ).__get_case__(self.start_case_id, auth_header)
            case["fraud_prediction"] = fraud_predictions.get(
                str(self.start_case_id), None
            )

            suggestions = super().generate(case)
            suggestions = remove_cases_from_list(suggestions, [case])
            suggestions = suggestions[: self.target_length - 1]
            suggestions = [case] + suggestions

            return suggestions

        # If no location is given, generate all possible lists, and choose the best one
        cases = self.__get_eligible_cases__()
        if not cases:
            logger.warning("No eligible cases, could not generate best list")
            return []

        topped_cases = cases
        if hasattr(
            self.settings.day_settings.team_settings, "top_cases_count"
        ) and getattr(self.settings.day_settings.team_settings, "top_cases_count"):
            for c in cases:
                c["fraud_prediction"] = fraud_predictions.get(str(c.get("id")), {})
                c["score"] = self.get_score(c)
            topped_cases = sorted(cases, key=lambda case: case["score"], reverse=True)
            logger.info("Algorithm: use top_cases_count")
            logger.info([c.get("id") for c in topped_cases][:50])
            topped_cases = topped_cases[
                : self.settings.day_settings.team_settings.top_cases_count
            ]

        # Run in parallel processes to improve speed
        jobs = multiprocessing.cpu_count()

        # Multiprocessing sometimes freezes during local development.
        # SSL error: decryption failed or bad record mac
        # Use threads instead by setting LOCAL_DEVELOPMENT_USE_THREADS to True in .env
        if settings.LOCAL_DEVELOPMENT_USE_THREADS:
            candidates = Parallel(n_jobs=jobs, prefer="threads")(
                delayed(self.parallelized_function)(
                    case, cases, fraud_predictions, index
                )
                for index, case in enumerate(topped_cases)
            )
        else:
            candidates = Parallel(n_jobs=jobs, backend="multiprocessing")(
                delayed(self.parallelized_function)(
                    case, cases, fraud_predictions, index
                )
                for index, case in enumerate(topped_cases)
            )

        best_list = self.get_best_list(candidates)
        best_list = sorted(best_list, key=lambda case: case["distance"])

        return best_list
