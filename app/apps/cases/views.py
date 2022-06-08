import logging
from datetime import datetime

import requests
from apps.cases.serializers import DecosPermitSerializer, PermitCheckmarkSerializer
from apps.cases.swagger_parameters import case_search_parameters
from apps.fraudprediction.utils import get_fraud_prediction
from apps.itinerary.models import Itinerary
from apps.itinerary.serializers import ItineraryTeamMemberSerializer
from apps.users.auth_apps import AZAKeyAuth
from apps.users.utils import get_keycloak_auth_header_from_request
from apps.visits.models import Visit
from apps.visits.serializers import VisitSerializer
from django.conf import settings
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from keycloak_oidc.drf.permissions import IsInAuthorizedRealm
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from utils import queries_bag_api as bag_api
from utils import queries_brk_api as brk_api
from utils.queries_decos_api import DecosJoinRequest
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
        bag_id = data.get("address", {}).get("bag_id")

        day_settings_id = (
            case_instance.day_settings.id if case_instance.day_settings else None
        )
        data.update(
            {
                "bag_data": bag_api.get_bag_data_by_bag_id(data.get("address")),
                "brk_data": brk_api.get_brk_data(bag_id),
                "fraud_prediction": get_fraud_prediction(case_id),
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

        data = case.fetch_events(get_keycloak_auth_header_from_request(request))

        return Response(data)


class CaseSearchViewSet(ViewSet):
    """
    A temporary search ViewSet for listing cases
    """

    def __add_fraud_prediction__(self, cases):
        """
        Enriches the cases with fraud predictions
        """
        cases = cases.copy()

        for case in cases:
            case_id = str(case.get("id"))
            case["fraud_prediction"] = get_fraud_prediction(case_id)

        return cases

    def __add_teams__(self, cases, itineraries_created_at):
        """
        Enriches the cases with teams
        """
        # Enrich the search result data with teams whose itinerary contains this item
        mapped_cases = {}
        cases = cases.copy()

        for case in cases:
            # Map the objects so that they're easily accessible through the case_id
            case_id = str(case.get("id"))
            mapped_cases[case_id] = case
            # Add a teams arrar to the case object as well
            case["teams"] = []

        # Get today's itineraries
        itineraries = Itinerary.objects.filter(created_at=itineraries_created_at).all()

        for itinerary in itineraries:
            team = itinerary.team_members.all()
            itinerary_cases = itinerary.get_cases()

            # Match the mapped_cases to the itinerary_cases, and add the teams
            for case in itinerary_cases:
                case_id = case.case_id
                mapped_case = mapped_cases.get(case_id, {"teams": []})
                serialized_team = ItineraryTeamMemberSerializer(team, many=True)
                mapped_case["teams"].append(serialized_team.data)

        return cases

    def _clean_cases(self, cases):
        cases = [
            {
                **c,
                **{
                    "current_states": [
                        s
                        for s in c.get("current_states", [])
                        if s.get("status_name") in settings.AZA_CASE_STATE_NAMES
                    ]
                },
            }
            for c in cases
        ]
        return cases

    @extend_schema(
        parameters=case_search_parameters, description="Search query parameters"
    )
    def list(self, request):
        """
        Returns a list of cases found with the given parameters
        """

        if settings.USE_ZAKEN_MOCK_DATA:
            result = get_zaken_case_list()
        else:
            param_translate = {
                "streetName": "street_name",
                "streetNumber": "number",
                "suffix": "suffix",
                "postalCode": "postal_code",
            }
            url = f"{settings.ZAKEN_API_URL}/cases/"
            queryParams = {}
            queryParams.update(request.GET)

            queryParams = dict(
                (param_translate.get(k, k), v) for k, v in queryParams.items()
            )
            queryParams.update(
                {
                    "open_cases": True,
                    "page_size": 1000,
                    "task": ["task_uitvoeren_leegstandsgesprek", "task_create_visit"],
                }
            )
            response = requests.get(
                url,
                params=queryParams,
                timeout=60,
                headers=get_headers(get_keycloak_auth_header_from_request(request)),
            )
            response.raise_for_status()

            result = response.json().get("results", [])

            for case in result:
                Case.get(case_id=case.get("id"))

            cases = self.__add_fraud_prediction__(result)
            cases = self.__add_teams__(cases, datetime.now())
            cases = self._clean_cases(cases)
            return JsonResponse({"cases": cases})


bag_id = OpenApiParameter(
    name="bag_id",
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    required=True,
    description="Verblijfsobjectidentificatie",
)


class PermitViewSet(ViewSet):
    @extend_schema(
        parameters=[bag_id],
        description="Get permit checkmarks based on bag id",
        responses={200: PermitCheckmarkSerializer()},
    )
    @action(detail=False, url_name="permit checkmarks", url_path="checkmarks")
    def get_permit_checkmarks(self, request):
        bag_id = request.GET.get("bag_id")
        response = DecosJoinRequest().get_checkmarks_by_bag_id(bag_id)

        serializer = PermitCheckmarkSerializer(data=response)

        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.initial_data)

    @extend_schema(
        parameters=[bag_id],
        description="Get permit details based on bag id",
        responses={200: DecosPermitSerializer(many=True)},
    )
    @action(detail=False, url_name="permit details", url_path="details")
    def get_permit_details(self, request):
        bag_id = request.GET.get("bag_id")
        response = DecosJoinRequest().get_permits_by_bag_id(bag_id)

        serializer = DecosPermitSerializer(data=response, many=True)

        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.initial_data)
