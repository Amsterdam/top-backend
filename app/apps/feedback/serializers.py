from rest_framework import serializers


class FeedbackSerializer(serializers.Serializer):
    feedback = serializers.CharField()
    url = serializers.CharField()
    user_agent = serializers.CharField(required=False)
    screen = serializers.CharField(required=False)
