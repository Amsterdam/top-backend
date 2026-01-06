import json
import logging
from datetime import datetime

import requests
from apps.cases.serializers import CaseSearchSerializer
from apps.itinerary.models import Itinerary
from apps.itinerary.serializers import ItineraryTeamMemberSerializer
from apps.users.auth_apps import AZAKeyAuth
from apps.users.permissions import IsInAuthorizedRealm
from apps.users.utils import get_auth_header_from_request
from apps.visits.models import Visit
from apps.visits.serializers import VisitSerializer
from django.conf import settings
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from utils import queries_bag_api as bag_api
from utils import queries_brk_api as brk_api
from utils.queries_zaken_api import get_headers

from .mock import get_zaken_case_list
from .models import Case

logger = logging.getLogger(__name__)


class CaseViewSet(ViewSet):
    permission_classes = [IsInAuthorizedRealm | AZAKeyAuth]
    """
    A Viewset for showing a single Case in detail
    """

    def retrieve(self, request, pk):
        case_id = pk
        case_instance = Case.get(case_id)

        data = {
            "deleted": False,
        }
        data.update(model_to_dict(case_instance))
        data.update(case_instance.data_context({"request": request}))

        address = data.get("address", {})
        bag_id = address.get("bag_id")
        nummeraanduiding_id = address.get("nummeraanduiding_id")

        day_settings_id = (
            case_instance.day_settings.id if case_instance.day_settings else None
        )

        data.update(
            {
                "bag_data": bag_api.get_bag_data_by_nummeraanduiding_id(
                    nummeraanduiding_id
                ),
                "brk_data": brk_api.get_brk_data(bag_id),
                "day_settings_id": day_settings_id,
            }
        )

        return JsonResponse(data)

    @extend_schema(
        description="Lists all visits for this case",
        responses={200: VisitSerializer(many=True)},
    )
    @action(detail=True, methods=["get"], name="visits")
    def visits(self, request, pk):
        """
        Lists all visits for this case
        """

        case = get_object_or_404(Case, case_id=pk)

        visits = Visit.objects.filter(case_id=case)

        serializer = VisitSerializer(visits, many=True)

        return Response(serializer.data)

    @extend_schema(
        description="Lists all events for this case",
        responses={200: serializers.ListSerializer(child=serializers.DictField())},
    )
    @action(detail=True, methods=["get"], name="events")
    def events(self, request, pk):
        """
        Lists all events for this case
        """

        case = Case.get(case_id=pk)

        data = case.fetch_events(get_auth_header_from_request(request))

        return Response(data)


class BaseCaseSearchViewSet(ViewSet):
    """
    Shared base ViewSet for case search endpoints
    """

    def _add_teams(self, cases, itineraries_created_at):
        mapped_cases = {}
        cases = cases.copy()

        for case in cases:
            case_id = str(case.get("id"))
            mapped_cases[case_id] = case
            case["teams"] = []

        itineraries = Itinerary.objects.filter(created_at=itineraries_created_at).all()

        for itinerary in itineraries:
            team = itinerary.team_members.all()
            itinerary_cases = itinerary.get_cases()

            for case in itinerary_cases:
                case_id = case.case_id
                mapped_case = mapped_cases.get(case_id)
                if not mapped_case:
                    continue

                serialized_team = ItineraryTeamMemberSerializer(
                    team,
                    many=True,
                )
                mapped_case["teams"].append(serialized_team.data)

        return cases

    def _clean_cases(self, cases):
        return [
            {
                **c,
                "workflows": [
                    {"state": s.get("state")}
                    for s in c.get("workflows", [])
                    if s.get("state", {}).get("name") in settings.AZA_CASE_STATE_NAMES
                ],
            }
            for c in cases
        ]

    def get_cases_from_api(self, request):
        """
        Must be implemented by subclasses
        """
        raise NotImplementedError

    def list(self, request, *args, **kwargs):
        if settings.USE_ZAKEN_MOCK_DATA:
            cases = get_zaken_case_list()
        else:
            cases = self.get_cases_from_api(request)
            for case in cases:
                Case.get(case_id=case.get("id"))

        cases = self._add_teams(cases, datetime.now())
        cases = self._clean_cases(cases)

        return JsonResponse(cases, safe=False)


class CaseSearchViewSet(BaseCaseSearchViewSet):
    """
    Legacy search endpoint
    """

    serializer_class = CaseSearchSerializer

    def list(self, request, *args, **kwargs):
        response_list = super().list(request, *args, **kwargs).content
        cases = json.loads(response_list)
        return JsonResponse({"cases": cases})

    def get_cases_from_api(self, request):
        param_translate = {
            "streetName": "street_name",
            "streetNumber": "number",
            "suffix": "suffix",
            "postalCode": "postal_code",
        }

        queryParams = {param_translate.get(k, k): v for k, v in request.GET.items()}

        queryParams.update(
            {
                "open_cases": True,
                "page_size": 1000,
                "task": [
                    "task_uitvoeren_leegstandsgesprek",
                    "task_create_visit",
                ],
            }
        )

        response = requests.get(
            f"{settings.ZAKEN_API_URL}/cases/",
            params=queryParams,
            timeout=60,
            headers=get_headers(get_auth_header_from_request(request)),
        )
        response.raise_for_status()

        return response.json().get("results", [])


class CaseSearchV2ViewSet(BaseCaseSearchViewSet):
    """
    Search v2 endpoint for cases
    """

    serializer_class = CaseSearchSerializer

    def get(self, request, *args, **kwargs):
        cases = self._clean_cases(...)  # lijst van dicts
        serializer = self.get_serializer(cases, many=True)
        return Response(serializer.data)  # dit geeft direct een lijst terug

    def get_cases_from_api(self, request):
        allowed_params = {
            "page",
            "page_size",
            "theme_name",
            "address_search",
        }

        queryParams = {k: v for k, v in request.GET.items() if k in allowed_params}

        if "page_size" not in queryParams:
            queryParams["page_size"] = 1000

        queryParams.update(
            {
                "open_cases": True,
                "task": [
                    "task_uitvoeren_leegstandsgesprek",
                    "task_create_visit",
                ],
            }
        )

        response = requests.get(
            f"{settings.ZAKEN_API_URL}/cases/",
            params=queryParams,
            timeout=60,
            headers=get_headers(get_auth_header_from_request(request)),
        )
        response.raise_for_status()

        return response.json().get("results", [])
