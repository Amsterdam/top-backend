from apps.visits.models import Visit
from rest_framework import serializers


class VisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visit
        fields = "__all__"


class VisitRelatedSerializer(serializers.ModelSerializer):
    """
    Serializer for Visit m2m relation but with start_time added
    """

    class Meta:
        model = Visit
        fields = ["id", "start_time"]
