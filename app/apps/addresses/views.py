import requests
from apps.users.utils import get_keycloak_auth_header_from_request
from django.conf import settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from utils.queries_zaken_api import get_headers

from .serializers import (
    HousingCorporationSerializer,
    MeldingenSerializer,
    PowerbrowserSerializer,
)

bag_id = OpenApiParameter(
    name="bag_id",
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    required=True,
    description="Verblijfsobjectidentificatie",
)


def fetch_housing_corporations(auth_header=None):
    url = f"{settings.ZAKEN_API_URL}/addresses/housing-corporations/"

    response = requests.get(
        url,
        timeout=5,
        headers=get_headers(auth_header),
    )
    response.raise_for_status()

    return response.json().get("results", [])


def fetch_districts(auth_header=None):
    url = f"{settings.ZAKEN_API_URL}/addresses/districts/"

    response = requests.get(
        url,
        timeout=5,
        headers=get_headers(auth_header),
    )
    response.raise_for_status()

    return response.json().get("results", [])


def fetch_meldingen(bag_id, auth_header=None, query_params=None):
    url = f"{settings.ZAKEN_API_URL}/addresses/{bag_id}/meldingen/"

    response = requests.get(
        url, timeout=30, headers=get_headers(auth_header), params=query_params
    )

    return response.json(), response.status_code


def fetch_residents(bag_id, body, auth_header=None):
    url = f"{settings.ZAKEN_API_URL}/addresses/{bag_id}/residents/"
    print(body)
    response = requests.post(
        url, timeout=30, headers=get_headers(auth_header), json=body
    )

    return response.json(), response.status_code


def fetch_power_browser_permits(bag_id, auth_header=None):
    url = f"{settings.ZAKEN_API_URL}/addresses/{bag_id}/permits-powerbrowser/"
    response = requests.get(
        url,
        timeout=30,
        headers=get_headers(auth_header),
    )

    return response.json(), response.status_code


class AddressViewSet(ViewSet):
    lookup_field = "bag_id"

    @action(detail=True, url_name="decos", url_path="decos")
    def get_decos(self, request, bag_id):
        url = f"{settings.ZAKEN_API_URL}/addresses/{bag_id}/permits/"

        response = requests.get(
            url,
            timeout=30,
            headers={
                "Authorization": request.headers.get("Authorization"),
            },
        )
        response.raise_for_status()

        return Response(response.json())

    @extend_schema(
        description="Get B&B PowerBrowser permit details based on bag id",
        responses={status.HTTP_200_OK: PowerbrowserSerializer(many=True)},
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="permits-powerbrowser",
    )
    def power_browser_permits_by_bag_id(self, request, bag_id):
        data, status_code = fetch_power_browser_permits(
            bag_id, get_keycloak_auth_header_from_request(request)
        )
        return Response(data, status=status_code)

    @extend_schema(
        description="Gets the projects associated with the requested team",
        responses={status.HTTP_200_OK: HousingCorporationSerializer(many=True)},
    )
    @action(
        detail=False,
        url_path="housing-corporations",
        methods=["get"],
    )
    def housing_corporations(self, request):
        data = []

        serializer = HousingCorporationSerializer(
            fetch_housing_corporations(get_keycloak_auth_header_from_request(request)),
            many=True,
        )
        data = serializer.data

        return Response(data)

    @extend_schema(
        description="Gets all meldingen for holiday rental.",
        responses={status.HTTP_200_OK: MeldingenSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name="offset",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Page number.",
            ),
            OpenApiParameter(
                name="limit",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Number of items per page.",
            ),
            OpenApiParameter(
                name="start_date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Shows meldingen from the given date.",
            ),
            OpenApiParameter(
                name="end_date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Shows meldingen till the given date.",
            ),
        ],
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="meldingen",
    )
    def meldingen_by_bag_id(self, request, bag_id):
        data, status_code = fetch_meldingen(
            bag_id, get_keycloak_auth_header_from_request(request), request.query_params
        )
        return Response(data, status=status_code)

    @extend_schema(
        description="Gets the residents associated with the requested object",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "obo_access_token": {
                        "type": "string",
                        "description": "access_token for OBO-flow",
                    },
                },
                "required": ["obo_access_token"],
            }
        },
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="residents",
    )
    def residents_by_bag_id(self, request, bag_id):
        data, status_code = fetch_residents(
            bag_id, request.data, get_keycloak_auth_header_from_request(request)
        )
        return Response(data, status=status_code)

    @action(
        detail=False,
        methods=["get"],
        url_path="districts",
    )
    def get_districts(self, request):
        data = fetch_districts(get_keycloak_auth_header_from_request(request))
        return Response(data)
