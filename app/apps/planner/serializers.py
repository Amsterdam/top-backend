from apps.cases.serializers import Project, Stadium, StadiumLabelSerializer
from apps.planner.models import (
    DaySettings,
    PostalCodeRange,
    PostalCodeRangeSet,
    TeamSettings,
)
from apps.visits.serializers import (
    ObservationSerializer,
    SituationSerializer,
    SuggestNextVisitSerializer,
)
from django.conf import settings
from rest_framework import serializers
from rest_framework.relations import PKOnlyObject


class PlannerListSettingsSerializer(serializers.Serializer):
    length_of_list = serializers.IntegerField(
        required=False, min_value=1, max_value=20, default=8
    )
    primary_stadium = serializers.CharField(required=False)
    secondary_stadia = serializers.ListField(required=False)
    exclude_stadia = serializers.ListField(required=False)

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
    projects = serializers.ListField(required=True)
    postal_codes = PlannerPostalCodeSettingsSerializer(required=False, many=True)
    days = PlannerWeekSettingsSerializer(required=True)


class PostalCodeRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostalCodeRange
        fields = (
            "range_start",
            "range_end",
        )


class PostalCodeRangePresetSerializer(serializers.ModelSerializer):
    postal_code_ranges_presets = PostalCodeRangeSerializer(
        many=True, read_only=True, source="postal_code_ranges"
    )

    class Meta:
        model = PostalCodeRangeSet
        fields = (
            "id",
            "name",
            "postal_code_ranges_presets",
        )


class StringRelatedToIdField(serializers.PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        instances = self.queryset.filter(name=data)
        if instances and len(instances) == 1:
            return super().to_internal_value(instances.get().id)
        else:
            raise serializers.ValidationError("Object with name: %s not found" % data)

    def to_representation(self, data):
        if isinstance(data, PKOnlyObject):
            return self.queryset.get(id=data.pk).name
        return data.name


class TeamSettingsCompactSerializer(serializers.ModelSerializer):
    marked_stadia = StadiumLabelSerializer(read_only=True, many=True)
    situation_choices = serializers.ListField(read_only=True)
    observation_choices = ObservationSerializer(read_only=True, many=True)
    suggest_next_visit_choices = SuggestNextVisitSerializer(read_only=True, many=True)

    class Meta:
        model = TeamSettings
        fields = (
            "name",
            "use_zaken_backend",
            "zaken_team_name",
            "observation_choices",
            "situation_choices",
            "suggest_next_visit_choices",
            "fraud_prediction_model",
            "marked_stadia",
            "show_issuemelding",
            "show_vakantieverhuur",
            "show_vakantieverhuur",
        )


class DaySettingsCompactSerializer(serializers.ModelSerializer):
    team_settings = TeamSettingsCompactSerializer(read_only=True)
    week_day = serializers.IntegerField(read_only=True)

    class Meta:
        model = DaySettings
        fields = (
            "id",
            "name",
            "week_day",
            "team_settings",
        )


class TeamSchedules(serializers.Serializer):
    actions = serializers.ListField(read_only=True)
    day_segments = serializers.ListField(read_only=True)
    priorities = serializers.ListField(read_only=True)
    week_segments = serializers.ListField(read_only=True)


class DaySettingsSerializer(serializers.ModelSerializer):
    projects = StringRelatedToIdField(many=True, queryset=Project.objects.all())
    primary_stadium = StringRelatedToIdField(
        queryset=Stadium.objects.all(), allow_null=True, required=False
    )
    secondary_stadia = StringRelatedToIdField(many=True, queryset=Stadium.objects.all())
    exclude_stadia = StringRelatedToIdField(many=True, queryset=Stadium.objects.all())
    team_settings = TeamSettingsCompactSerializer(read_only=True)
    week_day = serializers.IntegerField(read_only=True, allow_null=True)
    team_schedules = TeamSchedules(read_only=True, allow_null=True)

    class Meta:
        model = DaySettings
        fields = (
            "id",
            "name",
            "week_day",
            "opening_date",
            "postal_code_ranges",
            "postal_code_ranges_presets",
            "length_of_list",
            "projects",
            "primary_stadium",
            "secondary_stadia",
            "exclude_stadia",
            "team_settings",
            "sia_presedence",
            "team_schedules",
        )

    def validate(self, data):
        data = super().validate(data)
        # clean projects based on real team settings choices
        data["projects"] = [
            project
            for project in data["projects"]
            if project in self.instance.team_settings.project_choices.all()
        ]

        # clean all stdium options based on real team settings choices
        data["primary_stadium"] = (
            data.get("primary_stadium")
            if data.get("primary_stadium")
            in self.instance.team_settings.stadia_choices.all()
            else None
        )

        data["secondary_stadia"] = [
            stadium
            for stadium in data["secondary_stadia"]
            if stadium in self.instance.team_settings.stadia_choices.all()
        ]
        data["exclude_stadia"] = [
            stadium
            for stadium in data["exclude_stadia"]
            if stadium in self.instance.team_settings.stadia_choices.all()
            and stadium not in data.get("secondary_stadia", [])
            and stadium != data.get("primary_stadium", [])
        ]
        return data


class TeamSettingsSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    situation_choices = serializers.ListField(read_only=True)
    observation_choices = ObservationSerializer(read_only=True, many=True)
    suggest_next_visit_choices = SuggestNextVisitSerializer(read_only=True, many=True)
    project_choices = serializers.StringRelatedField(read_only=True, many=True)
    stadia_choices = serializers.StringRelatedField(read_only=True, many=True)
    marked_stadia = StadiumLabelSerializer(read_only=True, many=True)
    day_settings_list = DaySettingsCompactSerializer(read_only=True, many=True)

    class Meta:
        model = TeamSettings
        fields = (
            "id",
            "name",
            "use_zaken_backend",
            "zaken_team_name",
            "observation_choices",
            "situation_choices",
            "suggest_next_visit_choices",
            "project_choices",
            "stadia_choices",
            "marked_stadia",
            "day_settings_list",
        )
