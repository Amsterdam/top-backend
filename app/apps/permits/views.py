import json
import logging
from datetime import datetime

import requests
from apps.cases.models import Case
from apps.permits.api_queries_decos_join import DecosJoinRequest
from apps.permits.forms import SearchForm
from apps.permits.serializers import DecosSerializer
from constance.backends.database.models import Constance
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ViewSet

bag_id = OpenApiParameter(
    name="bag_id",
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    required=True,
    description="Verblijfsobjectidentificatie",
)


class DecosViewSet(ViewSet):
    @extend_schema(
        parameters=[bag_id],
        description="Get decos data based on bag id",
        responses={200: DecosSerializer()},
    )
    @action(detail=False, url_name="details", url_path="details")
    def get_decos_entry_by_bag_id(self, request):
        bag_id = request.GET.get("bag_id")
        dt = datetime.strptime(
            request.GET.get("date", datetime.today().strftime("%Y-%m-%d")), "%Y-%m-%d"
        )

        if not bag_id:
            raise Http404

        response = DecosJoinRequest().get_decos_entry_by_bag_id(bag_id, dt)

        serializer = DecosSerializer(data=response)

        if serializer.is_valid(raise_exception=True):
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


class PermitViewSet(ViewSet):
    lookup_field = "bag_id"

    @extend_schema(
        parameters=[bag_id],
        description="Get decos data based on bag id",
        responses={200: serializers.Serializer()},
    )
    @action(detail=True, url_name="permits details", url_path="permits")
    def get_permit(self, request, bag_id):
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


class DecosAPISearch(UserPassesTestMixin, FormView):
    form_class = SearchForm
    template_name = "decos_search.html"
    success_url = "/admin/decos-api-search/"

    def get_context_data(self, **kwargs):
        kwargs["base_url"] = settings.DECOS_JOIN_API
        return super().get_context_data(**kwargs)

    def test_func(self):
        return self.request.user.is_superuser

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        dt = datetime.today()
        if form.is_valid():
            if form.cleaned_data.get("search_url"):
                response = DecosJoinRequest().get(form.cleaned_data.get("search_url"))
            elif (
                form.cleaned_data.get("bag_id")
                and form.cleaned_data.get("response_type") == "raw"
            ):
                response = DecosJoinRequest().get_decos_object_with_bag_id(
                    form.cleaned_data.get("bag_id")
                )
            elif (
                form.cleaned_data.get("bag_id")
                and form.cleaned_data.get("response_type") == "checkmarks"
            ):
                response = DecosJoinRequest().get_decos_entry_by_bag_id(
                    form.cleaned_data.get("bag_id"), dt
                )
                serializer = DecosSerializer(data=response)
                if serializer.is_valid():
                    response = serializer.data
                else:
                    response = {"serializer_error": "ERROR"}

            else:
                response = DecosJoinRequest().get("")

        context = self.get_context_data(**kwargs)
        context["form"] = form
        context["decos_data"] = json.dumps(response, indent=4)

        return self.render_to_response(context)
