from rest_framework import serializers


class HousingCorporationSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)


class MeldingenSerializer(serializers.Serializer):
    pageNumber = serializers.IntegerField()
    pageSize = serializers.IntegerField()
    totalPages = serializers.IntegerField()
    totalRecords = serializers.IntegerField()
    data = serializers.ListField(child=serializers.DictField())
