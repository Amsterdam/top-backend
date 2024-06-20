import logging

from apps.cases.models import Case
from apps.users.serializers import UserSerializer
from apps.visits.models import (
    Observation,
    Situation,
    SuggestNextVisit,
    Visit,
    VisitTeamMember,
)
from django.db import transaction
from rest_framework import serializers

from .tasks import push_visit

logger = logging.getLogger(__name__)


class SituationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Situation
        fields = [
            "value",
            "verbose",
        ]


class SuggestNextVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuggestNextVisit
        fields = [
            "value",
            "verbose",
        ]


class ObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observation
        fields = [
            "value",
            "verbose",
        ]


class VisitTeamMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = VisitTeamMember
        fields = (
            "id",
            "user",
        )


class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = ("id", "case_id")


class CaseField(serializers.RelatedField):
    def get_queryset(self):
        return Case.objects.all()

    def to_internal_value(self, data):
        return self.get_queryset().get(case_id=data)

    def to_representation(self, value):
        return CaseSerializer(value).data


class VisitSerializer(serializers.ModelSerializer):
    team_members = VisitTeamMemberSerializer(many=True, read_only=True)
    case_id = CaseField()
    completed = serializers.BooleanField(default=False)

    def is_valid(self, raise_exception=False):
        return super().is_valid(raise_exception)

    def _complete_visit_and_update_aza(self, instance):
        logger.info("TOP: Executed _complete_visit_and_update_aza")
        instance.capture_visit_meta_data()
        task = push_visit.s(visit_id=instance.id).delay
        transaction.on_commit(task)

    def create(self, validated_data):
        instance = super().create(validated_data)
        self._complete_visit_and_update_aza(instance)
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        self._complete_visit_and_update_aza(instance)
        return instance

    class Meta:
        model = Visit
        fields = "__all__"
