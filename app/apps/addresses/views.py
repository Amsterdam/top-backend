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

from .serializers import HousingCorporationSerializer

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


def fetch_residents(bag_id, auth_header=None):
    url = f"{settings.ZAKEN_API_URL}/addresses/{bag_id}/residents/"

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
            timeout=10,
            headers={
                "Authorization": request.headers.get("Authorization"),
            },
        )
        response.raise_for_status()

        return Response(response.json())

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

    @action(
        detail=True,
        methods=["get"],
        url_path="residents",
    )
    def residents_by_bag_id(self, request, bag_id):
        data, status_code = fetch_residents(
            bag_id, get_keycloak_auth_header_from_request(request)
        )
        return Response(data, status=status_code)
