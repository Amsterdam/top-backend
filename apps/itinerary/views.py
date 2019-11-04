from rest_framework import viewsets, mixins
from .models import Itinerary
from .serializers import ItinerarySerializer


class ItineraryViewSet(
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    """
    A simple ViewSet for listing itineraries.
    """
    queryset = Itinerary.objects.all()
    serializer_class = ItinerarySerializer
