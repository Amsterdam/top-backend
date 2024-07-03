from apps.itinerary.views import ItineraryItemViewSet, ItineraryViewSet, NoteViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"itineraries", ItineraryViewSet, basename="itinerary")
router.register(r"itinerary-items", ItineraryItemViewSet, basename="itinerary-item")
router.register(r"notes", NoteViewSet, basename="notes")
