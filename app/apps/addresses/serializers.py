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


class RegistrationDetailsSerializer(serializers.Serializer):
    registrationNumber = serializers.CharField(required=True)
    requester = serializers.DictField()
    rentalHouse = serializers.DictField()
    requestForOther = serializers.BooleanField()
    requestForBedAndBreakfast = serializers.BooleanField()
    createdAt = serializers.DateTimeField()
    agreementDate = serializers.DateTimeField()


class PowerbrowserSerializer(serializers.Serializer):
    baG_ID = serializers.CharField()
    product = serializers.CharField()
    kenmerk = serializers.CharField(allow_null=True)
    muT_DAT = serializers.DateTimeField()
    status = serializers.CharField()
    resultaat = serializers.CharField(allow_null=True)
    startdatum = serializers.DateTimeField()
    einddatum = serializers.DateTimeField(allow_null=True)
    vergunninghouder = serializers.CharField(allow_null=True)
    initator = serializers.CharField(allow_null=True)
    datuM_TOT = serializers.DateTimeField(allow_null=True)
