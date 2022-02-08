import logging
from datetime import datetime

from dateutil import parser
from django.utils import timezone
from geopy.distance import distance

logger = logging.getLogger(__name__)


# BWV
def filter_out_cases(cases, stadia=[]):
    """
    Returns a list of cases without the given stadia
    """
    if len(stadia) == 0:
        return cases

    def has_stadium(case):
        return case["stadium"] not in stadia

    return list(filter(lambda case: has_stadium(case), cases))


# BWV
def filter_cases(cases, stadia):
    """
    Returns a list of cases with the given stadia
    """
    if len(stadia) == 0:
        return cases

    def has_stadium(case):
        return case["stadium"] in stadia

    return list(filter(lambda case: has_stadium(case), cases))


# AZA and BWV
def remove_cases_from_list(cases, cases_to_remove):
    """
    Returns a new list without the 'cases_to_remove' items
    """
    cases_to_remove = [case.get("id") for case in cases_to_remove]

    def should_not_remove(case):
        return case.get("id") not in cases_to_remove

    new_list = list(filter(lambda case: should_not_remove(case), cases))

    return new_list


# AZA and BWV
def get_case_coordinates(cases):
    """
    Maps the cases to an array of coordinates
    """
    coordinates = list(
        map(
            lambda case: [
                case.get("address").get("lat"),
                case.get("address").get("lng"),
            ],
            cases,
        )
    )

    return coordinates


# AZA and BWV
def calculate_geo_distances(center, cases):
    """
    Returns a set of distances in KM from the given center
    """
    case_coordinates = get_case_coordinates(cases)
    distances = [
        distance(center, coordinates).km * 1000 for coordinates in case_coordinates
    ]

    return distances


# BWV
def filter_cases_with_missing_coordinates(cases):
    """
    Cases with polluted data (missing coordinates) are removed
    """

    def has_coordinates(case):
        address = case.get("address", {})
        return address.get("lat", None) and address.get("lng", None)

    return list(filter(lambda case: has_coordinates(case), cases))


# AZA and BWV
def filter_cases_with_postal_code(cases, ranges=[]):
    """
    Returns a list of cases for which the postal code falls within the given start and end range
    """

    if not ranges:
        return cases

    def is_in_range(case, range):
        range_start = range.get("range_start")
        range_end = range.get("range_end")

        if range_start > range_end:
            raise ValueError("Start range can't be larger than end_range")
        postal_code = case.get("address", {}).get("postal_code")
        postal_code_numbers = int(postal_code[:4])

        return range_start <= postal_code_numbers <= range_end

    def is_in_ranges(case, ranges):
        for range in ranges:
            if is_in_range(case, range):
                return True
        return False

    cases = filter(lambda case: is_in_ranges(case, ranges), cases)
    return list(cases)


# AZA
def filter_out_incompatible_cases(cases):
    return [
        c
        for c in cases
        if c.get("address", {}).get("lat") and c.get("address", {}).get("lng")
    ]


# AZA
def filter_schedules(cases, team_schedules):
    schedule_keys = [
        ["day_segment", "day_segments"],
        ["week_segment", "week_segments"],
    ]

    def case_in_schedule(case):
        valid = True
        for key_set in schedule_keys:
            if not set(team_schedules.get(key_set[1], [])).intersection(
                set(
                    [
                        schedule.get(key_set[0], {}).get("id", 0)
                        for schedule in case.get("schedules", [])
                    ]
                )
            ):
                valid = False

        visit_from_datetime = case.get("schedules", [{}])[0].get("visit_from_datetime")
        if visit_from_datetime:
            try:
                visit_from_datetime = parser.parse(visit_from_datetime)
                if timezone.now() < (visit_from_datetime):
                    valid = False
            except Exception as e:
                logger.error(f"visit_from_datetime e: {str(e)}")
        return valid

    return [c for c in cases if case_in_schedule(c)]


# AZA
def filter_reasons(cases, reasons):
    return [c for c in cases if c.get("reason", {}).get("id", 0) in reasons]


# AZA
def filter_state_types(cases, state_types):
    return [
        case
        for case in cases
        if set(
            [c.get("status", 0) for c in case.get("current_states", [])]
        ).intersection(set(state_types))
    ]


# AZA
def is_day_of_this_year_odd():
    day_of_year = datetime.now().timetuple().tm_yday
    return (day_of_year % 2) == 1


# AZA
def get_cases_with_odd_or_even_ids(cases, odd=False):
    return [c for c in cases if (int(c.get("id") % 2) == (1 if odd else 0))]
