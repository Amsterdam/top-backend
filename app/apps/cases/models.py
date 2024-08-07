import datetime

import requests
from apps.fraudprediction.models import FraudPrediction
from apps.users.utils import get_keycloak_auth_header_from_request
from django.conf import settings
from django.db import models
from django.utils import timezone
from utils.queries_zaken_api import get_headers

from .mock import get_zaken_case_list

CASE_404 = {
    "deleted": True,
    "address": {
        "street_name": "Zaak verwijderd",
        "number": 404,
    },
}


class Case(models.Model):
    class Meta:
        ordering = ["case_id"]

    """
    A simple case model
    """
    case_id = models.CharField(max_length=255, null=True, blank=False)
    is_top_bwv_case = models.BooleanField(default=True)

    def get(case_id):
        return Case.objects.get_or_create(
            case_id=case_id,
        )[0]

    def fetch_case(self, auth_header=None):
        from apps.itinerary.models import Itinerary

        url = f"{settings.ZAKEN_API_URL}/cases/{self.case_id}/"
        queryParams = {
            "open_cases": True,
            "page_size": 1000,
        }
        response = requests.get(
            url,
            timeout=10,
            params=queryParams,
            headers=get_headers(auth_header),
        )
        if response.status_code == 404:
            return CASE_404

        response.raise_for_status()

        case_data = response.json()

        used_cases_ids = [
            case.case_id for case in Itinerary.get_cases_for_date(timezone.now().date())
        ]
        current_task_names = [
            task.get("task_name")
            for workflow in case_data["workflows"]
            for task in workflow.get("tasks", [])
        ]
        allowed_task_names = [
            task_name
            for task_name in current_task_names
            if task_name in settings.AZA_ALLOWED_TASK_NAMES
        ]

        if str(case_data["id"]) not in used_cases_ids and not allowed_task_names:
            return CASE_404

        case_data["workflows"] = [
            state
            for state in case_data["workflows"]
            if str(state.get("state", {}).get("name")) in settings.AZA_CASE_STATE_NAMES
        ]
        case_data.update({"deleted": False})
        return case_data

    def fetch_events(self, auth_header=None):
        url = f"{settings.ZAKEN_API_URL}/cases/{self.case_id}/events/"

        response = requests.get(
            url,
            timeout=20,
            headers=get_headers(auth_header),
        )
        response.raise_for_status()

        return response.json()

    def __get_case__(self, case_id, auth_header=None):
        if settings.USE_ZAKEN_MOCK_DATA:
            return dict((str(c.get("id")), c) for c in get_zaken_case_list()).get(
                case_id, {}
            )
        return self.fetch_case(auth_header)

    def get_location(self, auth_header=None):
        case_data = self.__get_case__(self.case_id, auth_header)
        address = case_data.get("address")
        return {"lat": address.get("lat"), "lng": address.get("lng")}

    @property
    def data(self):
        return self.__get_case__(self.case_id)

    def data_context(self, context):
        auth_header = None
        try:
            auth_header = get_keycloak_auth_header_from_request(
                context.get("request", {})
            )
        except Exception:
            pass
        return self.__get_case__(self.case_id, auth_header)

    @property
    def itinerary(self):
        now = datetime.datetime.now()
        itinerary_items = self.cases.filter(
            itinerary__created_at__gte=datetime.datetime(now.year, now.month, now.day)
        )
        if itinerary_items:
            return itinerary_items[0].itinerary
        return None

    @property
    def day_settings(self):
        return self.itinerary.settings.day_settings if self.itinerary else None

    @property
    def fraud_prediction(self):
        fraud_prediction = FraudPrediction.objects.get(case_id=self.case_id)
        return fraud_prediction

    def __str__(self):
        if self.case_id:
            return self.case_id
        return ""
