import logging
import multiprocessing

import requests
from apps.cases.mock import get_zaken_case_list
from apps.cases.models import Case
from apps.fraudprediction.utils import get_fraud_predictions
from apps.planner.algorithm.base import (
    ItineraryGenerateAlgorithm,
    filter_cases_with_postal_code,
)
from apps.planner.const import MAX_SUGGESTIONS_COUNT, SCORING_WEIGHTS
from apps.planner.mock import get_team_reasons, get_team_schedules, get_team_state_types
from apps.planner.models import Weights
from apps.planner.utils import (
    calculate_geo_distances,
    filter_out_incompatible_cases,
    filter_reasons,
    filter_schedules,
    filter_state_types,
    remove_cases_from_list,
)
from django.conf import settings
from joblib import Parallel, delayed
from settings.const import ISSUEMELDING
from utils.queries import get_case
from utils.queries_zaken_api import get_headers

logger = logging.getLogger(__name__)


def get_eligible_cases_v2(generator):
    logger.info("v2 __get_eligible_cases__")
    if settings.USE_ZAKEN_MOCK_DATA:
        cases = get_zaken_case_list()
        team_schedules = get_team_schedules()
        reasons = get_team_reasons()
        state_types = get_team_state_types()
    else:
        state_types = generator.settings.day_settings.fetch_team_state_types()
        team_schedules = generator.settings.day_settings.fetch_team_schedules()
        reasons = generator.settings.day_settings.fetch_team_reasons()

        url = f"{settings.ZAKEN_API_URL}/cases/"
        queryParams = {
            "openCases": "true",
            "openStatus": ",".join([str(state.get("id", 0)) for state in state_types]),
            "theme": generator.settings.day_settings.team_settings.zaken_team_name,
            "startDate": generator.settings.opening_date.strftime("%Y-%m-%d"),
            "noPagination": "true",
        }

        response = requests.get(
            url,
            params=queryParams,
            timeout=5,
            headers=get_headers(),
        )
        response.raise_for_status()

        cases = response.json()

    logger.info("initial case count")
    logger.info(len(cases))
    logger.info("validate team_schedules")
    team_schedules = (
        dict(
            (
                k,
                [
                    s
                    for s in getattr(generator.settings, k)
                    if s in [ss.get("id", 0) for ss in v]
                ],
            )
            for k, v in team_schedules.items()
            if k
            in [
                "day_segments",
                "week_segments",
            ]
        )
        if team_schedules
        else {}
    )
    logger.info("validate reasons")
    reasons = [
        r
        for r in generator.settings.reasons
        if r in [reason.get("id", 0) for reason in reasons]
    ]
    logger.info("validate state_types")
    state_types = [state.get("id", 0) for state in state_types]
    state_types_selected = [
        st for st in generator.settings.state_types if st in state_types
    ]
    logger.info("selected algorithm states")
    logger.info(state_types_selected)
    cases = filter_out_incompatible_cases(cases)
    logger.info("after filter_out_incompatible_cases")
    logger.info(len(cases))
    cases = filter_schedules(cases, team_schedules)
    logger.info("after filter_schedules")
    logger.info(len(cases))
    cases = filter_state_types(cases, state_types)
    logger.info("after filter_state_types")
    logger.info(len(cases))
    cases = filter_cases_with_postal_code(cases, generator.postal_code_ranges)
    logger.info("after filter_cases_with_postal_code")
    logger.info(len(cases))
    cases = [
        c
        for c in cases
        if str(c.get("id"))
        not in [str(case.get("id")) for case in generator.exclude_cases]
    ]
    logger.info("after remove_cases_from_list")
    logger.info(len(cases))

    return cases


class ItineraryKnapsackSuggestions(ItineraryGenerateAlgorithm):
    def __init__(self, settings, postal_code_settings=[], settings_weights=None):
        super().__init__(settings, postal_code_settings)

        self.weights = Weights()

        if settings_weights:
            self.weights = Weights(
                distance=settings_weights.distance,
                fraud_probability=settings_weights.fraud_probability,
                reason=settings_weights.reason,
                state_types=settings_weights.state_types,
                priority=settings_weights.priority,
                primary_stadium=settings_weights.primary_stadium,
                secondary_stadium=settings_weights.secondary_stadium,
                issuemelding=settings_weights.issuemelding,
                is_sia=settings_weights.is_sia,
            )

    def get_score(self, case):
        """
        Gets the score of the given case
        """
        distance = case.get("normalized_inverse_distance", 0)

        fraud_probability = case.get("fraud_prediction", {}).get("fraud_probability", 0)
        priority = case.get("schedules", [{}])[0].get("priority", {}).get("weight", 0)

        reason = (
            case.get("reason", {}).get("id", 0) in self.settings.reasons
            if self.settings.reasons
            else []
        )
        state_types = set(
            [case.get("status") for case in case.get("current_states", [])]
        ).intersection(
            set(self.settings.state_types if self.settings.state_types else [])
        )
        stadium = case.get("stadium")
        has_primary_stadium = stadium == self.primary_stadium
        has_secondary_stadium = stadium in self.secondary_stadia
        has_issuemelding_stadium = stadium == ISSUEMELDING

        score = self.weights.score(
            distance,
            fraud_probability,
            bool(reason),
            bool(state_types),
            priority,
            has_primary_stadium,
            has_secondary_stadium,
            has_issuemelding_stadium,
            bool(case.get("is_sia") == "J"),
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
            case_id = case.get("id")
            case["distance"] = distances[index]
            case["normalized_inverse_distance"] = (
                (max_distance - case["distance"]) / max_distance if max_distance else 0
            )
            case["fraud_prediction"] = fraud_predictions.get(case_id, {})
            case["score"] = self.get_score(case)

        # Sort the cases based on score
        sorted_cases = sorted(cases, key=lambda case: case["score"], reverse=True)

        return sorted_cases[:MAX_SUGGESTIONS_COUNT]


class ItineraryKnapsackSuggestionsV1(ItineraryKnapsackSuggestions):
    pass


class ItineraryKnapsackSuggestionsV2(ItineraryKnapsackSuggestions):
    def __get_eligible_cases__(self):
        return get_eligible_cases_v2(self)


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

    def generate(self):
        fraud_predictions = get_fraud_predictions()
        if self.start_case_id:
            case = Case.get(
                case_id=self.start_case_id,
                is_top_bwv_case=not self.settings.day_settings.team_settings.use_zaken_backend,
            ).__get_case__(self.start_case_id)
            case["fraud_prediction"] = fraud_predictions.get(self.start_case_id, None)

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
                c["fraud_prediction"] = fraud_predictions.get(c.get("id"), {})
                c["score"] = self.get_score(c)
            topped_cases = sorted(cases, key=lambda case: case["score"], reverse=True)
            logger.info("Algorithm: use top_cases_count")
            logger.info([c.get("score") for c in topped_cases][:50])
            topped_cases = topped_cases[
                : self.settings.day_settings.team_settings.top_cases_count
            ]

        # Run in parallel processes to improve speed
        jobs = multiprocessing.cpu_count()

        # multiprocessing freezes during local sometimes, option is trying threads insteads
        # candidates = Parallel(n_jobs=jobs, prefer="threads")(

        candidates = Parallel(n_jobs=jobs, backend="multiprocessing")(
            delayed(self.parallelized_function)(case, cases, fraud_predictions, index)
            for index, case in enumerate(topped_cases)
        )

        best_list = self.get_best_list(candidates)
        best_list = sorted(best_list, key=lambda case: case["distance"])

        return best_list


class ItineraryKnapsackListV1(ItineraryKnapsackList):
    pass


class ItineraryKnapsackListV2(ItineraryKnapsackList):
    def __get_eligible_cases__(self):
        return get_eligible_cases_v2(self)
