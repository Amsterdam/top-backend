from apps.planner.models import TeamSettings
from apps.planner.serializers import TeamSettingsSerializer as TeamSettingsSerializer
from rest_framework import serializers


class TeamSettingsIdSerializer(TeamSettingsSerializer):
    class Meta:
        model = TeamSettings
        fields = (
            "id",
            "team_type",
        )


class UserIdSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    email = serializers.EmailField(read_only=True)
    username = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    full_name = serializers.CharField()
    team_settings = TeamSettingsIdSerializer(many=True)
    # current_team_settings_id = serializers.IntegerField()


class UserSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    email = serializers.EmailField(required=True)
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    full_name = serializers.CharField()
    team_settings = TeamSettingsIdSerializer(many=True)
    # current_team_settings_id = serializers.IntegerField()
