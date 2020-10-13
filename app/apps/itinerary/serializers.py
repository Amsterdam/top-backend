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
from apps.planner.const import TEAM_TYPE_SETTINGS
from apps.planner.models import TeamSettings
from apps.planner.serializers import TeamSettingsSerializer
from apps.users.serializers import UserIdSerializer, UserSerializer
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
    projects = ProjectSerializer(many=True)
    team_settings = TeamSettingsSerializer()
    primary_stadium = StadiumSerializer()
    secondary_stadia = StadiumSerializer(many=True)
    exclude_stadia = StadiumSerializer(many=True)
    start_case = CaseSimpleSerializer(required=False)

    class Meta:
        model = ItinerarySettings
        fields = (
            "opening_date",
            "team_settings",
            "target_length",
            "projects",
            "primary_stadium",
            "secondary_stadia",
            "exclude_stadia",
            "start_case",
        )


class ItineraryItemSerializer(serializers.ModelSerializer):
    case = CaseSerializer(read_only=True)
    notes = NoteSerializer(read_only=True, many=True)
    visits = VisitSerializer(read_only=True, many=True, source="get_visits_for_day")

    class Meta:
        model = ItineraryItem
        fields = ("id", "position", "notes", "case", "visits", "checked")


class ItineraryItemUpdateSerializer(serializers.ModelSerializer):
    position = serializers.FloatField(required=False)

    class Meta:
        model = ItineraryItem
        fields = ("id", "position", "checked")


class ItineraryItemCreateSerializer(serializers.ModelSerializer):
    case_id = serializers.CharField(required=True)
    position = serializers.FloatField(required=False)

    class Meta:
        model = ItineraryItem
        fields = ("itinerary", "case_id", "position")

    def create(self, validated_data):
        case_id = validated_data.get("case_id")
        itinerary_id = validated_data.get("itinerary")
        position = validated_data.get("position", None)

        itinerary = Itinerary.objects.get(id=itinerary_id)
        itinerary_item = itinerary.add_case(case_id, position)

        return itinerary_item


class ItineraryTeamMemberSerializer(serializers.ModelSerializer):
    user = UserIdSerializer(read_only=True)

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

    def __get_stadia_from_settings__(self, settings, list_name):
        """ Returns a list of Stadium objects from settings """
        team_settings_stadia = TEAM_TYPE_SETTINGS[
            settings["team_settings"]["team_type"]["name"]
        ].get("stadia_choices")
        stadia = settings.get(list_name, [])
        stadia = [
            stadium.get("name")
            for stadium in stadia
            if stadium.get("name") in team_settings_stadia
        ]
        stadia = [Stadium.get(name=stadium) for stadium in stadia]

        return stadia

    def __get_stadium_from_settings__(self, settings, name):
        """ Returns a single Stadium object from settings """
        team_settings_stadia = TEAM_TYPE_SETTINGS[
            settings["team_settings"]["team_type"]["name"]
        ].get("stadia_choices")
        if (
            settings.get(name)
            and settings.get(name, {}).get("name") in team_settings_stadia
        ):
            stadium = settings.get(name).get("name")
            stadium = Stadium.get(name=stadium)

            return stadium

    def __get_projects_from_settings__(self, settings):
        """ Returns the Projects objects from settings """
        team_settings_projects = TEAM_TYPE_SETTINGS[
            settings["team_settings"]["team_type"]["name"]
        ].get("project_choices")
        projects = settings.get("projects", [])
        projects = [
            project.get("name")
            for project in projects
            if project.get("name") in team_settings_projects
        ]
        projects = [Project.get(name=project) for project in projects]

        return projects

    def __get_start_case_from_settings__(self, settings):
        """ Returns a Case object from the settings """
        try:
            case_dict = settings.get("start_case", None)
            case_id = case_dict.get("case_id", None)
            case = Case.get(case_id)
            return case
        except Exception:
            return None

    def create(self, validated_data):
        itinerary = Itinerary.objects.create()

        # Add team members to the itinerary
        team_members = validated_data.get("team_members", [])
        team_members = [
            team_member.get("user").get("id") for team_member in team_members
        ]
        itinerary.add_team_members(team_members)
        print(validated_data)
        settings = validated_data.get("settings")
        opening_date = settings.get("opening_date")
        target_length = settings.get("target_length")

        # Get the projects and stadia from settings
        projects = self.__get_projects_from_settings__(settings)
        primary_stadium = self.__get_stadium_from_settings__(
            settings, "primary_stadium"
        )
        secondary_stadia = self.__get_stadia_from_settings__(
            settings, "secondary_stadia"
        )
        exclude_stadia = self.__get_stadia_from_settings__(settings, "exclude_stadia")
        start_case = self.__get_start_case_from_settings__(settings)

        # First create the settings
        itinerary_settings = ItinerarySettings.objects.create(
            opening_date=opening_date,
            itinerary=itinerary,
            primary_stadium=primary_stadium,
            target_length=target_length,
            start_case=start_case,
            team_settings=TeamSettings.objects.get(
                id=settings.get("team_settings").get("id")
            ),
        )

        # Next, add the many-to-many relations of the itinerary_Settings
        itinerary_settings.projects.set(projects)
        itinerary_settings.secondary_stadia.set(secondary_stadia)
        itinerary_settings.exclude_stadia.set(exclude_stadia)

        # Get the postal code ranges from the settings
        postal_code_settings = validated_data.get("postal_code_settings", [])
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
