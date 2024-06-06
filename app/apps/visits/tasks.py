import logging

import requests
from celery import shared_task
from django.conf import settings
from utils.queries_zaken_api import get_headers

from .models import Visit

logger = logging.getLogger(__name__)

DEFAULT_RETRY_DELAY = 10
CONNECT_TIMEOUT = 10
READ_TIMEOUT = 60


def get_serialized_visit(visit_id):
    from .serializers import VisitSerializer

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

    case = data.pop("case_id")
    data["case"] = case["case_id"]
    data["top_visit_id"] = visit_id

    return data


@shared_task(bind=True, default_retry_delay=DEFAULT_RETRY_DELAY)
def push_visit(self, visit_id, auth_header=None, task_name_ids=[]):
    logger.info(f"Pushing visit {visit_id} to AZA")

    url = f"{settings.ZAKEN_API_URL}/visits/"

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
        logger.exception(f"Pushing visit {visit_id} to AZA failed")
        self.retry(exc=exception)

    return f"visit_id: {visit_id}"
