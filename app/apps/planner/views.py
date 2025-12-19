import datetime
import sys

from apps.itinerary.models import Itinerary
from apps.planner.models import DaySettings, TeamSettings
from apps.planner.serializers import (
    CaseProjectSerializer,
    CaseReasonSerializer,
    CaseStateTypeSerializer,
    CaseSubjectSerializer,
    CaseTagSerializer,
    DaySettingsCompactSerializer,
    DaySettingsSerializer,
    NewDaySettingsSerializer,
    TeamScheduleTypesSerializer,
    TeamSettingsSerializer,
    TeamSettingsThemeSerializer,
)
from apps.users.utils import get_auth_header_from_request
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.management import call_command
from django.http import Http404, HttpResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from settings.const import DAY_SETTING_IN_USE


class TeamSettingsViewSet(ModelViewSet):
    """
    A view for listing/adding/updating/removing a TeamSettings
    """

    serializer_class = TeamSettingsSerializer
    queryset = TeamSettings.objects.filter(enabled=True)

    @extend_schema(
        description="Gets the reasons associated with the requested team",
        responses={status.HTTP_200_OK: CaseReasonSerializer(many=True)},
    )
    @action(
        detail=True,
        url_path="reasons",
        methods=["get"],
    )
    def reasons(self, request, pk):
        team_settings = self.get_object()
        data = []

        serializer = CaseReasonSerializer(
            team_settings.fetch_team_reasons(get_auth_header_from_request(request)),
            many=True,
        )
        data = serializer.data

        return Response(data)

    @extend_schema(
        description="Gets the Scheduling Types associated with the given team",
        responses={status.HTTP_200_OK: TeamScheduleTypesSerializer()},
    )
    @action(
        detail=True,
        url_path="schedule-types",
        methods=["get"],
    )
    def schedule_types(self, request, pk):
        team_settings = self.get_object()
        data = {}

        serializer = TeamScheduleTypesSerializer(
            team_settings.fetch_team_schedules(get_auth_header_from_request(request))
        )
        data = serializer.data

        return Response(data)

    @extend_schema(
        description="Gets the CaseStateTypes associated with the given team",
        responses={status.HTTP_200_OK: CaseStateTypeSerializer(many=True)},
    )
    @action(
        detail=True,
        url_path="state-types",
        methods=["get"],
    )
    def state_types(self, request, pk):
        data = []

        serializer = CaseStateTypeSerializer(
            settings.AZA_CASE_STATE_TYPES,
            many=True,
        )
        data = serializer.data

        return Response(data)

    @extend_schema(
        description="Gets the projects associated with the requested team",
        responses={status.HTTP_200_OK: CaseProjectSerializer(many=True)},
    )
    @action(
        detail=True,
        url_path="case-projects",
        methods=["get"],
    )
    def projects(self, request, pk):
        team_settings = self.get_object()
        data = []

        serializer = CaseProjectSerializer(
            team_settings.fetch_projects(get_auth_header_from_request(request)),
            many=True,
        )
        data = serializer.data

        return Response(data)

    @extend_schema(
        description="Gets the subjects associated with the requested team",
        responses={status.HTTP_200_OK: CaseSubjectSerializer(many=True)},
    )
    @action(
        detail=True,
        url_path="subjects",
        methods=["get"],
    )
    def subjects(self, request, pk):
        team_settings = self.get_object()
        data = []

        serializer = CaseSubjectSerializer(
            team_settings.fetch_subjects(get_auth_header_from_request(request)),
            many=True,
        )
        data = serializer.data

        return Response(data)

    @extend_schema(
        description="Gets the tags associated with the requested team",
        responses={status.HTTP_200_OK: CaseTagSerializer(many=True)},
    )
    @action(
        detail=True,
        url_path="tags",
        methods=["get"],
    )
    def tags(self, request, pk):
        team_settings = self.get_object()
        data = []

        serializer = CaseTagSerializer(
            team_settings.fetch_tags(get_auth_header_from_request(request)),
            many=True,
        )
        data = serializer.data

        return Response(data)

    @extend_schema(
        description="Gets the day settings for a specific day of the week",
        parameters=[
            OpenApiParameter(
                "day",
                OpenApiTypes.INT,
                OpenApiParameter.PATH,
                description="Day of the week (0=Monday, 6=Sunday)",
            ),
        ],
        responses={status.HTTP_200_OK: DaySettingsCompactSerializer(many=True)},
    )
    @action(
        detail=True,
        url_path="weekday/(?P<day>[0-6])",
        methods=["get"],
    )
    def weekday(self, request, pk, **kwargs):
        day_index = int(kwargs.get("day"))

        team_settings = self.get_object()
        result = DaySettings.objects.filter(
            team_settings=team_settings, week_days__contains=[day_index]
        )
        serializer = DaySettingsCompactSerializer(result, many=True)

        return Response(serializer.data)


@extend_schema(
    parameters=[
        OpenApiParameter("case-count", OpenApiTypes.DATE, OpenApiParameter.QUERY),
    ]
)
class DaySettingsViewSet(ModelViewSet):
    """
    A view for listing/adding/updating/removing a DaySettings
    """

    serializer_class = DaySettingsSerializer
    queryset = DaySettings.objects.all()

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if not Itinerary.objects.filter(
                settings__day_settings=instance,
                created_at=datetime.datetime.now().strftime("%Y-%m-%d"),
            ):
                self.perform_destroy(instance)
            else:
                raise ValidationError(DAY_SETTING_IN_USE, 404)
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return NewDaySettingsSerializer
        return DaySettingsSerializer

    @extend_schema(
        description="Gets the cases count based on these day settings",
        responses={status.HTTP_200_OK: serializers.DictField()},
    )
    @action(
        detail=True,
        url_path="case-count",
        methods=["get"],
    )
    def case_count(self, request, pk):
        obj = self.get_object()
        data = obj.fetch_cases_count(get_auth_header_from_request(request))
        return Response(data)


@user_passes_test(lambda u: u.is_superuser)
def dumpdata(request):
    sysout = sys.stdout
    fname = "%s-%s.json" % ("top-planner", datetime.datetime.now().strftime("%Y-%m-%d"))
    response = HttpResponse(content_type="application/json")
    response["Content-Disposition"] = "attachment; filename=%s" % fname

    sys.stdout = response
    call_command(
        "dumpdata",
        "planner",
        "visits.Situation",
        "visits.Observation",
        "visits.SuggestNextVisit",
        "--indent=4",
    )
    sys.stdout = sysout

    return response


class TeamSettingsThemesViewSet(ModelViewSet):
    """
    Gets all themes from team-settings
    """

    serializer_class = TeamSettingsThemeSerializer
    queryset = TeamSettings.objects.filter(enabled=True)
    http_method_names = ["get"]
