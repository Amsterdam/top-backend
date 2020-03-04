from rest_framework import serializers

class UserSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    email = serializers.EmailField(required=True)
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
