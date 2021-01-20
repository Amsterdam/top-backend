import json
import logging

from apps.permits.api_queries_decos_join import DecosJoinRequest
from apps.permits.serializers import DecosPermitSerializer, PermitCheckmarkSerializer
from constance.backends.database.models import Constance
from django.conf import settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

bag_id = OpenApiParameter(
    name="bag_id",
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    required=True,
    description="Verblijfsobjectidentificatie",
)

DEFAULT_PERMIT = {
    "has_b_and_b_permit": "False",
    "has_vacation_rental_permit": "False",
    "has_splitsing_permit": "False",
    "has_samenvoeging_permit": "False",
    "has_woonvorming_permit": "False",
    "has_omzettings_permit": "False",
    "has_ligplaats_permit": "False",
}


class PermitViewSet(ViewSet):
    @extend_schema(
        parameters=[bag_id],
        description="Get permit checkmarks based on bag id",
        responses={200: PermitCheckmarkSerializer()},
    )
    @action(detail=False, url_name="permit checkmarks", url_path="checkmarks")
    def get_permit_checkmarks(self, request):
        bag_id = request.GET.get("bag_id")
        # response = DecosJoinRequest().get_checkmarks_by_bag_id(bag_id)
        key = settings.CONSTANCE_PERMIT_DATA
        data, created = Constance.objects.get_or_create(key=key)
        try:
            data = json.load(data.value)
        except Exception:
            data = {}
        data = data.get(bag_id, DEFAULT_PERMIT)
        serializer = PermitCheckmarkSerializer(data=data)

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

    @extend_schema(description="test connection with decos")
    @action(detail=False, url_name="test decos connection", url_path="test-connect")
    def get_test_decos_connect(self, request):
        import requests

        response = requests.get(
            "https://decosdvl.acc.amsterdam.nl/decosweb/aspx/api/v1/"
        )

        if response.ok:
            return Response(response)
        return False
