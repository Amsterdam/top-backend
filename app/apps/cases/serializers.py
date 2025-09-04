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
        return obj.data_context(self.context)
