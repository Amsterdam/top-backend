from apps.planner.models import TeamSettings
from django.conf import settings
from rest_framework import serializers
from settings.const import PROJECTS, STADIA

from .const import TEAM_TYPE_SETTINGS


class PlannerListSettingsSerializer(serializers.Serializer):
    length_of_list = serializers.IntegerField(
        required=False, min_value=1, max_value=20, default=8
    )
    primary_stadium = serializers.ChoiceField(required=False, choices=STADIA)
    secondary_stadia = serializers.MultipleChoiceField(required=False, choices=STADIA)
    exclude_stadia = serializers.MultipleChoiceField(required=False, choices=STADIA)

    def validate_mutual_exclusivity(self, stadia_a, stadia_b, message):
        for stadium in stadia_a:
            if stadium in stadia_b:
                raise serializers.ValidationError(message)

    def validate_does_not_contain(self, stadium, stadia, message):
        if stadium in stadia:
            raise serializers.ValidationError(message)

    def validate(self, data):
        secondary_stadia = data.get("secondary_stadia", [])
        exclude_stadia = data.get("exclude_stadia", [])
        error_message = (
            "exclude_stadia and secondary_stadia should be mutually exclusive"
        )
        self.validate_mutual_exclusivity(
            secondary_stadia, exclude_stadia, error_message
        )

        primary_stadium = data.get("primary_stadium", None)
        if primary_stadium:
            error_message = "The primary_stadium cannot be in exclude_stadia "
            self.validate_does_not_contain(
                primary_stadium, exclude_stadia, error_message
            )

        return data


class PlannerDaySettingsSerializer(serializers.Serializer):
    day = PlannerListSettingsSerializer(required=False, many=False)
    evening = PlannerListSettingsSerializer(required=False, many=False)


class PlannerWeekSettingsSerializer(serializers.Serializer):
    monday = PlannerDaySettingsSerializer(required=True)
    tuesday = PlannerDaySettingsSerializer(required=True)
    wednesday = PlannerDaySettingsSerializer(required=True)
    thursday = PlannerDaySettingsSerializer(required=True)
    friday = PlannerDaySettingsSerializer(required=True)
    saturday = PlannerDaySettingsSerializer(required=True)
    sunday = PlannerDaySettingsSerializer(required=True)


class PlannerPostalCodeSettingsSerializer(serializers.Serializer):
    range_start = serializers.IntegerField(
        required=True,
        min_value=settings.CITY_MIN_POSTAL_CODE,
        max_value=settings.CITY_MAX_POSTAL_CODE,
    )

    range_end = serializers.IntegerField(
        required=True,
        min_value=settings.CITY_MIN_POSTAL_CODE,
        max_value=settings.CITY_MAX_POSTAL_CODE,
    )

    def validate(self, data):
        range_start = data.get("range_start")
        range_end = data.get("range_end")

        if range_end < range_start:
            raise serializers.ValidationError(
                "The start range can't be higher than the end range"
            )

        return data


class PlannerSettingsSerializer(serializers.Serializer):
    opening_date = serializers.DateField(required=True)
    projects = serializers.MultipleChoiceField(required=True, choices=PROJECTS)
    postal_codes = PlannerPostalCodeSettingsSerializer(required=False, many=True)
    days = PlannerWeekSettingsSerializer(required=True)


class TeamTypeSerializer(serializers.DictField):
    def to_representation(self, instance):
        return TEAM_TYPE_SETTINGS.get(instance)


class TeamSettingsSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    team_type = TeamTypeSerializer(read_only=True, required=False)
    settings = serializers.JSONField(required=True)

    class Meta:
        model = TeamSettings
        fields = (
            "id",
            "name",
            "team_type",
            "settings",
        )

    @property
    def data(self):
        data = super().data
        data["projects"] = data.get("team_type").get("project_choices")
        data["stadia"] = data.get("team_type").get("stadia_choices")
        return data

    def validate(self, data):
        data = super().validate(data)
        settings = PlannerSettingsSerializer(data=data.get("settings"), required=True)
        if not settings.is_valid():
            raise serializers.ValidationError("Wrong settings format")
        return data
