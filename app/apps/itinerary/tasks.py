import logging

import requests
from apps.itinerary.models import ItineraryItem
from apps.visits.models import Visit
from apps.visits.serializers import VisitSerializer
from celery import shared_task
from django.conf import settings
from sentry_sdk import capture_message
from utils.queries import get_case, get_import_stadia
from utils.queries_bag_api import get_bag_id
from utils.queries_zaken_api import (
    assert_allow_push,
    date_to_string,
    get_headers,
    stadium_bwv_to_push_state,
)

logger = logging.getLogger(__name__)

DEFAULT_RETRY_DELAY = 10
CONNECT_TIMEOUT = 10
READ_TIMEOUT = 60


@shared_task(bind=True, default_retry_delay=DEFAULT_RETRY_DELAY)
def push_itinerary_item(self, pk):
    """
    Pushing the itinerary and case date is needed
    """
    logger.info(f"Pushing case for itinerary item {pk}")
    assert_allow_push()

    itinerary_item = ItineraryItem.objects.get(pk=pk)

    case_id = itinerary_item.case.case_id
    case = get_case(case_id)

    start_date = date_to_string(case.get("start_date"))
    end_date = date_to_string(case.get("end_date", None))

    stadia = get_import_stadia(case_id)
    states = [stadium_bwv_to_push_state(stadium) for stadium in stadia]

    team_members = itinerary_item.itinerary.team_members.all()
    users = [team_member.user.email for team_member in team_members]

    data = {
        "identification": case_id,
        "case_type": case["case_reason"],
        "bag_id": get_bag_id(case),
        "start_date": start_date,
        "states": states,
        "users": users,
    }

    if end_date:
        data["end_date"] = end_date

    url = f"{settings.ZAKEN_API_URL}/push/"

    try:
        response = requests.post(
            url,
            timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            json=data,
            headers=get_headers(),
        )
        response.raise_for_status()

        response_json = response.json()

        itinerary_item.external_state_id = response_json["state"]["id"]
        itinerary_item.save()

        logger.info(f"Finished pushing case {case_id}")

        return response
    except Exception as exception:
        self.retry(exc=exception)


@shared_task(bind=True, default_retry_delay=DEFAULT_RETRY_DELAY)
def update_external_state(self, state_id, team_member_emails):
    logger.info(f"Updating external state {state_id} in zaken")

    assert_allow_push()

    url = f"{settings.ZAKEN_API_URL}/case-states/{state_id}/update-from-top/"
    data = {"user_emails": team_member_emails}

    try:
        response = requests.post(
            url,
            timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            json=data,
            headers=get_headers(),
        )
        response.raise_for_status()

    except Exception as exception:
        self.retry(exc=exception)

    logger.info(f"Finished updating external state {state_id}")


def update_external_states(itinerary):
    itinerary_items = itinerary.items.all()

    for itinerary_item in itinerary_items:
        team_members = itinerary.team_members.all()
        team_member_emails = [team_member.user.email for team_member in team_members]
        state_id = itinerary_item.external_state_id

        if state_id:
            update_external_state.delay(state_id, team_member_emails)


def get_serialized_visit(visit_id):
    visit = Visit.objects.get(id=visit_id)
    serializer = VisitSerializer(visit)
    data = serializer.data

    #  Reset author and team_members due to race condition
    data.pop("author")
    data.pop("team_members")

    team_members = visit.itinerary_item.itinerary.team_members.all()
    authors = [{"email": team_member.user.email} for team_member in team_members]
    data["authors"] = authors
    data["notes"] = data.pop("description", None)

    # Set the case id
    case = data.pop("case_id")
    data["case"] = case["case_id"]

    return data


@shared_task(bind=True, default_retry_delay=DEFAULT_RETRY_DELAY)
def push_visit(self, visit_id, created=False, auth_header=None):
    # logger.info(f"Pushing visit {visit_id} to AZA")
    capture_message(f"Pushing visit {visit_id} to AZA")
    assert_allow_push()
    url = f"{settings.ZAKEN_API_URL}/visits/"

    if not created:
        logger.info("AZA does not support updating visits anymore.")
        return f"AZA does not support updating visits anymore: visit_id: {visit_id}, created: {created}"

    data = get_serialized_visit(visit_id)

    try:
        response = requests.post(
            url,
            timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            json=data,
            headers=get_headers(auth_header),
        )
        response.raise_for_status()
    except Exception as exception:
        self.retry(exc=exception)

    return f"visit_id: {visit_id}, created: {created}"
