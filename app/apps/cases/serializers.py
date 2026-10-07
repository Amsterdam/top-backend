from apps.cases.models import Case
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers


class CaseSimpleSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="case_id")

    class Meta:
        model = Case
        fields = ("id",)


class CaseAddress(serializers.Serializer):
    bag_id = serializers.CharField(required=True)


class CaseWorkflowStateSerializer(serializers.Serializer):
    name = serializers.CharField(source="state.name")


class IdNameSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class CaseSearchSerializer(serializers.Serializer):
    id = serializers.CharField(source="case_id")
    address = CaseAddress(read_only=True)
    reason = IdNameSerializer()
    workflows = CaseWorkflowStateSerializer(many=True)
    project = IdNameSerializer(required=False, allow_null=True)
    subjects = IdNameSerializer(many=True)
    tags = IdNameSerializer(many=True)


class CaseSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="case_id")
    data = serializers.SerializerMethodField(method_name="get_data")

    class Meta:
        model = Case
        fields = ("id", "data")

    @extend_schema_field(serializers.DictField())
    def get_data(self, obj):
        # Prefer pre-fetched batch data to avoid per-item external requests
        cache = self.context.get("cases_data_cache")
        if cache is not None:
            data = cache.get(str(obj.case_id))
            if data is not None:
                return data
        return obj.data_context(self.context)
