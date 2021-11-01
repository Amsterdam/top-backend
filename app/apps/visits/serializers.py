from apps.cases.models import Case
from apps.users.serializers import UserSerializer
from apps.users.utils import get_keycloak_auth_header_from_request
from apps.visits.models import (
    Observation,
    Situation,
    SuggestNextVisit,
    Visit,
    VisitTeamMember,
)
from django.db import transaction
from rest_framework import serializers


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
    task_name_ids = None

    def is_valid(self, raise_exception=False):
        self.task_name_ids = self.initial_data.pop("task_name_ids", None)
        return super().is_valid(raise_exception)

    def _complete_visit_and_update_aza(self, instance, created):
        from apps.itinerary.tasks import push_visit

        instance.capture_visit_meta_data()
        auth_header = get_keycloak_auth_header_from_request(self.context.get("request"))
        task = push_visit.s(
            visit_id=instance.id,
            created=created,
            auth_header=auth_header,
            task_name_ids=self.task_name_ids,
        ).delay
        transaction.on_commit(task)

    def create(self, validated_data):
        instance = super().create(validated_data)
        if self.task_name_ids:
            self._complete_visit_and_update_aza(instance, True)
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if self.task_name_ids:
            self._complete_visit_and_update_aza(instance, False)
        return instance

    class Meta:
        model = Visit
        fields = "__all__"
