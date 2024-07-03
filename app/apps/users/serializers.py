from apps.planner.models import TeamSettings
from rest_framework import serializers


class UserTeamSettingsIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamSettings
        fields = ("id",)


class UserSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    email = serializers.EmailField(required=True)
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    full_name = serializers.CharField()
    team_settings = UserTeamSettingsIdSerializer(many=True)
