from rest_framework import serializers


class PassthroughSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError("Expected a JSON object.")
        return data

    def to_representation(self, instance):
        return instance


class PuntentellerAddressSerializer(PassthroughSerializer):
    pass


class PuntentellerInvoerwaardenSerializer(PassthroughSerializer):
    pass


class PuntentellingSerializer(PassthroughSerializer):
    pass
