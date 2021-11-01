import logging
from datetime import datetime

import requests
from apps.cases.models import Project
from apps.cases.serializers import (
    CaseEventSerializer,
    CaseSearchSerializer,
    DecosJoinFolderFieldsResponseSerializer,
    DecosJoinObjectFieldsResponseSerializer,
    DecosPermitSerializer,
    PermitCheckmarkSerializer,
    UnplannedCasesSerializer,
    get_decos_join_mock_folder_fields,
    get_decos_join_mock_object_fields,
)
from apps.cases.swagger_parameters import case_search_parameters, unplanned_parameters
from apps.fraudprediction.utils import add_fraud_predictions, get_fraud_prediction
from apps.itinerary.models import Itinerary
from apps.itinerary.serializers import CaseSerializer, ItineraryTeamMemberSerializer
from apps.planner.models import TeamSettings
from apps.users.auth_apps import AZAKeyAuth
from apps.users.utils import get_keycloak_auth_header_from_request
from apps.visits.models import Visit
from apps.visits.serializers import VisitSerializer
from django.conf import settings
from django.forms.models import model_to_dict
from django.http import HttpResponseBadRequest, HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from keycloak_oidc.drf.permissions import IsInAuthorizedRealm
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from utils import queries as q
from utils import queries_bag_api as bag_api
from utils import queries_brk_api as brk_api
from utils.queries_decos_api import DecosJoinRequest
from utils.queries_zaken_api import get_headers

from .mock import get_zaken_case_list, get_zaken_case_search_result_list
from .models import Case

logger = logging.getLogger(__name__)


class CaseViewSet(ViewSet):
    permission_classes = [IsInAuthorizedRealm | AZAKeyAuth]
    """
    A Viewset for showing a single Case in detail
    """

    def retrieve(self, request, pk):
        case_id = pk
        case_instance = Case.get(case_id, bool(str(case_id).find("_") >= 0))

        if case_instance.is_top_bwv_case:
            related_case_ids = q.get_related_case_ids(case_id)

            wng_id = related_case_ids.get("wng_id", None)
            adres_id = related_case_ids.get("adres_id", None)

            if not wng_id or not adres_id:
                return HttpResponseNotFound("Case not found")

            # Get the bag_data first in order to retrieve the 'verblijfsobjectidentificatie' id
            bag_data = bag_api.get_bag_data(wng_id)
            bag_id = bag_data.get("verblijfsobjectidentificatie")

            day_settings_id = (
                case_instance.day_settings.id if case_instance.day_settings else None
            )

            data = {
                "deleted": False,
                "bwv_hotline_bevinding": q.get_bwv_hotline_bevinding(wng_id),
                "bwv_hotline_melding": q.get_bwv_hotline_melding(wng_id),
                "bwv_personen": q.get_bwv_personen(adres_id),
                "address": q.get_import_adres(wng_id),
                "import_stadia": q.get_import_stadia(case_id),
                "bwv_tmp": q.get_bwv_tmp(case_id, adres_id),
                "statements": q.get_statements(case_id),
                "vakantie_verhuur": q.get_rental_information(wng_id),
                "bag_data": bag_data,
                "brk_data": brk_api.get_brk_data(bag_id),
                "related_cases": q.get_related_cases(adres_id),
                "fraud_prediction": get_fraud_prediction(case_id),
                "day_settings_id": day_settings_id,
                "is_sia": case_instance.data.get("is_sia"),
            }
        else:
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

    @extend_schema(parameters=unplanned_parameters, description="Unplanned Cases")
    @action(detail=False, methods=["get"], name="unplanned")
    def unplanned(self, request):
        """ Returns a list of unplanned cases, based on the given date and stadium """
        serializer = UnplannedCasesSerializer(data=request.GET)
        is_valid = serializer.is_valid()

        if not is_valid:
            return JsonResponse(
                {"message": "Could not validate data", "errors": serializer.errors},
                status=HttpResponseBadRequest.status_code,
            )

        date = request.GET.get("date")
        stadium = request.GET.get("stadium")
        itinerary = Itinerary.objects.filter(id=request.GET.get("itinerary_id"))
        projects = (
            list(
                itinerary.first()
                .settings.day_settings.team_settings.project_choices.all()
                .values_list("name", flat=True)
            )
            if itinerary
            else list(Project.objects.all().values_list("name", flat=True))
        )

        unplanned_cases = Itinerary.get_unplanned_cases(date, stadium, projects)
        cases = add_fraud_predictions(unplanned_cases)

        return JsonResponse({"cases": cases})

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
        responses={200: CaseEventSerializer()},
    )
    @action(detail=True, methods=["get"], name="events")
    def events(self, request, pk):
        """
        Lists all events for this case
        """

        case = Case.get(case_id=pk, is_top_bwv_case=False)
        serializer = CaseEventSerializer(
            case.fetch_events(get_keycloak_auth_header_from_request(request)), many=True
        )

        return Response(serializer.data)


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

    @extend_schema(
        parameters=case_search_parameters, description="Search query parameters"
    )
    def list(self, request):
        """
        Returns a list of cases found with the given parameters
        """

        if request.version == "v1":
            # TODO: Replace query parameter strings with constants
            postal_code = request.GET.get("postalCode", None)
            street_name = request.GET.get("streetName", "")
            street_number = request.GET.get("streetNumber", None)
            suffix = request.GET.get("suffix", "")

            if postal_code is None and street_name == "":
                return HttpResponseBadRequest(
                    "Missing postal code or street name is required"
                )
            elif not street_number:
                return HttpResponseBadRequest("Missing street number is required")
            else:
                cases = q.get_search_results(
                    postal_code, street_number, suffix, street_name
                )
                cases = self.__add_fraud_prediction__(cases)
                cases = self.__add_teams__(cases, datetime.now())

                return JsonResponse({"cases": cases})
        else:
            if settings.USE_ZAKEN_MOCK_DATA:
                result = get_zaken_case_list()
            else:
                url = f"{settings.ZAKEN_API_URL}/cases/search/"
                queryParams = {}
                queryParams.update(request.GET)

                response = requests.get(
                    url,
                    params=queryParams,
                    timeout=30,
                    headers=get_headers(get_keycloak_auth_header_from_request(request)),
                )
                response.raise_for_status()

                result = response.json().get("results", [])

            for case in result:
                Case.get(case_id=case.get("id"), is_top_bwv_case=False)

            cases = self.__add_fraud_prediction__(result)
            cases = self.__add_teams__(cases, datetime.now())
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
