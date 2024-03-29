import logging
from datetime import datetime

from dateutil import parser
from django.utils import timezone
from geopy.distance import distance

logger = logging.getLogger(__name__)


# AZA
def remove_cases_from_list(cases, cases_to_remove):
    """
    Returns a new list without the 'cases_to_remove' items
    """
    cases_to_remove = [str(case.get("id")) for case in cases_to_remove]

    def should_not_remove(case):
        return str(case.get("id")) not in cases_to_remove

    new_list = list(filter(lambda case: should_not_remove(case), cases))

    return new_list


# AZA
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


# AZA
def calculate_geo_distances(center, cases):
    """
    Returns a set of distances in KM from the given center
    """
    case_coordinates = get_case_coordinates(cases)
    distances = [
        distance(center, coordinates).km * 1000 for coordinates in case_coordinates
    ]

    return distances


# AZA
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
        visit_from_datetime = (
            case.get("schedules")[0].get("visit_from_datetime")
            if case.get("schedules")
            else None
        )
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
def is_day_of_this_year_odd():
    day_of_year = datetime.now().timetuple().tm_yday
    return (day_of_year % 2) == 1


# AZA
def get_cases_with_odd_or_even_ids(cases, odd=False):
    return [c for c in cases if (int(c.get("id") % 2) == (1 if odd else 0))]
