from rest_framework import serializers
from .models import Itinerary, ItineraryItem

class ItineraryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItineraryItem
        fields = ('case_id', 'address', 'postal_code_area', 'postal_code_street')

class ItinerarySerializer(serializers.ModelSerializer):
    items = ItineraryItemSerializer(many=True, read_only=True)

    class Meta:
        model = Itinerary
        fields = ('items',)
