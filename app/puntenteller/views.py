import requests
from apps.users.utils import get_auth_header_from_request
from django.conf import settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from utils.queries_zaken_api import get_headers

from .serializers import (
    PuntentellerAddressSerializer,
    PuntentellerInvoerwaardenSerializer,
    PuntentellingSerializer,
)

bag_id_parameter = OpenApiParameter(
    name="bag_id",
    type=OpenApiTypes.STR,
    location=OpenApiParameter.PATH,
    required=True,
    description="BAG identifier.",
)

limit_parameter = OpenApiParameter(
    name="limit",
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    required=False,
    description="Number of results to return per page.",
)

offset_parameter = OpenApiParameter(
    name="offset",
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    required=False,
    description="The initial index from which to return the results.",
)

puntentelling_id_parameter = OpenApiParameter(
    name="id",
    type=OpenApiTypes.INT,
    location=OpenApiParameter.PATH,
    required=True,
    description="Puntentelling identifier.",
)


def _parse_response(response):
    try:
        return response.json()
    except ValueError:
        return None


def _proxy_request(method, path, auth_header=None, params=None, body=None):
    response = requests.request(
        method=method,
        url=f"{settings.ZAKEN_API_URL}{path}",
        timeout=30,
        headers=get_headers(auth_header),
        params=params,
        json=body,
    )

    return _parse_response(response), response.status_code


class PuntentellerViewSet(ViewSet):
    @extend_schema(
        description="Get puntenteller data for an address.",
        parameters=[bag_id_parameter, limit_parameter, offset_parameter],
        responses={status.HTTP_200_OK: PuntentellerAddressSerializer},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path=r"adressen/(?P<bag_id>[^/.]+)",
    )
    def address(self, request, bag_id=None):
        data, status_code = _proxy_request(
            "get",
            f"/puntenteller/adressen/{bag_id}/",
            auth_header=get_auth_header_from_request(request),
            params=request.query_params,
        )
        return Response(data, status=status_code)

    @extend_schema(
        description="Create puntenteller data for an address.",
        parameters=[bag_id_parameter],
        request=PuntentellerAddressSerializer,
        responses={status.HTTP_200_OK: PuntentellerAddressSerializer},
    )
    @address.mapping.post
    def create_address(self, request, bag_id=None):
        serializer = PuntentellerAddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data, status_code = _proxy_request(
            "post",
            f"/puntenteller/adressen/{bag_id}/",
            auth_header=get_auth_header_from_request(request),
            body=serializer.validated_data,
        )
        return Response(data, status=status_code)

    @extend_schema(
        description="Get puntenteller invoerwaarden for an address.",
        parameters=[bag_id_parameter],
        responses={status.HTTP_200_OK: PuntentellerInvoerwaardenSerializer},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path=r"adressen/(?P<bag_id>[^/.]+)/invoerwaarden",
    )
    def invoerwaarden(self, request, bag_id=None):
        data, status_code = _proxy_request(
            "get",
            f"/puntenteller/adressen/{bag_id}/invoerwaarden/",
            auth_header=get_auth_header_from_request(request),
            params=request.query_params,
        )
        return Response(data, status=status_code)

    @extend_schema(
        description="Get a puntentelling.",
        parameters=[puntentelling_id_parameter],
        responses={status.HTTP_200_OK: PuntentellingSerializer},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path=r"puntentellingen/(?P<id>[^/.]+)",
    )
    def puntentelling(self, request, id=None):
        data, status_code = _proxy_request(
            "get",
            f"/puntenteller/puntentellingen/{id}/",
            auth_header=get_auth_header_from_request(request),
            params=request.query_params,
        )
        return Response(data, status=status_code)

    @extend_schema(
        description="Partially update a puntentelling.",
        parameters=[puntentelling_id_parameter],
        request=PuntentellingSerializer,
        responses={status.HTTP_200_OK: PuntentellingSerializer},
    )
    @puntentelling.mapping.patch
    def partial_update_puntentelling(self, request, id=None):
        serializer = PuntentellingSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        data, status_code = _proxy_request(
            "patch",
            f"/puntenteller/puntentellingen/{id}/",
            auth_header=get_auth_header_from_request(request),
            body=serializer.validated_data,
        )
        return Response(data, status=status_code)
