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


class CaseSearchSerializer(serializers.Serializer):
    id = serializers.CharField(source="case_id")
    address = CaseAddress(read_only=True)


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


class CaseWorkflowStateSerializer(serializers.Serializer):
    name = serializers.CharField(source="state.name")


class CaseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = ()

    def to_representation(self, obj):
        """
        Retrieves the full case data from the cache or data_context,
        but reduces workflows to a list containing only state.name.
        """

        cache = self.context.get("cases_data_cache")

        if cache is not None:
            data = cache.get(str(obj.case_id))
        else:
            data = obj.data_context(self.context)

        if not isinstance(data, dict):
            return {}

        # Transformeer workflows naar alleen de namen
        workflows = data.get("workflows", [])
        data["workflows"] = [
            wf["state"]["name"]
            for wf in workflows
            if "state" in wf and "name" in wf["state"]
        ]

        return data
