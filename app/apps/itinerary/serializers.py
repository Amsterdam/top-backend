from apps.cases.models import Case, Project, Stadium
from apps.cases.serializers import (
    CaseSerializer,
    CaseSimpleSerializer,
    ProjectSerializer,
    StadiumSerializer,
)
from apps.itinerary.models import (
    Itinerary,
    ItineraryItem,
    ItinerarySettings,
    ItineraryTeamMember,
    Note,
    PostalCodeSettings,
)
from apps.planner.models import DaySettings
from apps.planner.serializers import DaySettingsSerializer
from apps.users.serializers import UserSerializer
from apps.visits.serializers import VisitSerializer
from rest_framework import serializers


class NoteCrudSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Note
        fields = ("id", "text", "itinerary_item", "author")


class NoteSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Note
        fields = ("id", "text", "author")


class PostalCodeSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostalCodeSettings
        fields = ("range_start", "range_end")


class ItinerarySettingsSerializer(serializers.ModelSerializer):
    day_settings = DaySettingsSerializer()
    start_case = CaseSimpleSerializer(required=False)

    # BWV data below
    projects = ProjectSerializer(many=True)
    primary_stadium = StadiumSerializer()
    secondary_stadia = StadiumSerializer(many=True)
    exclude_stadia = StadiumSerializer(many=True)

    class Meta:
        model = ItinerarySettings
        fields = (
            "opening_date",
            "day_settings",
            "target_length",
            "start_case",
            "day_segments",
            "week_segments",
            "priorities",
            "reasons",
            "state_types",
            "project_ids",
            "housing_corporations",
            # BWV data below
            "projects",
            "primary_stadium",
            "secondary_stadia",
            "exclude_stadia",
        )


class ItineraryItemSerializer(serializers.ModelSerializer):
    case = CaseSerializer(read_only=True)
    notes = NoteSerializer(read_only=True, many=True)
    visits = VisitSerializer(read_only=True, many=True, source="get_visits_for_day")

    class Meta:
        model = ItineraryItem
        fields = ("id", "position", "notes", "case", "visits")


class ItineraryItemUpdateSerializer(serializers.ModelSerializer):
    position = serializers.FloatField(required=False)

    class Meta:
        model = ItineraryItem
        fields = ("id", "position")


class ItineraryItemCreateSerializer(serializers.ModelSerializer):
    id = serializers.CharField(required=True)
    position = serializers.FloatField(required=False)

    class Meta:
        model = ItineraryItem
        fields = ("itinerary", "id", "position")

    def create(self, validated_data):
        case_id = validated_data.get("id")
        itinerary_id = validated_data.get("itinerary")
        position = validated_data.get("position", None)

        itinerary = Itinerary.objects.get(id=itinerary_id)
        itinerary_item = itinerary.add_case(case_id, position)

        return itinerary_item


class ItineraryTeamMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ItineraryTeamMember
        fields = (
            "id",
            "user",
        )


class ItinerarySerializer(serializers.ModelSerializer):
    items = ItineraryItemSerializer(read_only=True, many=True)
    created_at = serializers.DateField(read_only=True)
    team_members = ItineraryTeamMemberSerializer(many=True)
    settings = ItinerarySettingsSerializer(read_only=True)
    postal_code_settings = PostalCodeSettingsSerializer(
        read_only=True, many=True, required=False
    )

    def __get_start_case__(self, case_id, team_settings):
        """Returns a Case object"""
        if case_id:
            return Case.get(case_id)
        return None

    def create(self, validated_data):
        itinerary = Itinerary.objects.create()
        # Add team members to the itinerary
        team_members = validated_data.get("team_members", [])
        team_members = [
            team_member.get("user").get("id") for team_member in team_members
        ]
        itinerary.add_team_members(team_members)
        day_settings = DaySettings.objects.get(id=validated_data.get("day_settings_id"))
        opening_date = day_settings.opening_date
        target_length = validated_data.get("target_length")

        start_case = self.__get_start_case__(
            validated_data.get("start_case", {}).get("id"),
            day_settings.team_settings,
        )

        # First create the settings
        itinerary_settings = ItinerarySettings.objects.create(
            opening_date=opening_date,
            itinerary=itinerary,
            primary_stadium=day_settings.primary_stadium,
            target_length=target_length,
            start_case=start_case,
            day_settings=day_settings,
            sia_presedence=day_settings.sia_presedence,
            day_segments=day_settings.day_segments,
            week_segments=day_settings.week_segments,
            priorities=day_settings.priorities,
            project_ids=day_settings.project_ids,
            housing_corporations=day_settings.housing_corporations,
            housing_corporation_combiteam=day_settings.housing_corporation_combiteam,
            reasons=day_settings.reasons,
            state_types=day_settings.state_types,
        )

        # Next, add the many-to-many relations of the itinerary_Settings
        itinerary_settings.projects.set(day_settings.projects.all())
        itinerary_settings.secondary_stadia.set(day_settings.secondary_stadia.all())
        itinerary_settings.exclude_stadia.set(day_settings.exclude_stadia.all())

        # Get the postal code ranges from the settings
        postal_code_ranges_presets = [
            pcr
            for pcrp in day_settings.postal_code_ranges_presets.all()
            for pcr in pcrp.postal_code_ranges.all().values()
        ]
        postal_code_settings = (
            postal_code_ranges_presets
            if postal_code_ranges_presets
            else day_settings.postal_code_ranges
        )
        for postal_code_setting in postal_code_settings:
            range_start = postal_code_setting.get("range_start")
            range_end = postal_code_setting.get("range_end")

            PostalCodeSettings.objects.create(
                itinerary=itinerary,
                range_start=range_start,
                range_end=range_end,
            )

        return itinerary

    class Meta:
        model = Itinerary
        fields = (
            "id",
            "created_at",
            "team_members",
            "items",
            "settings",
            "postal_code_settings",
        )
