from apps.visits.views import ObservationViewSet, SuggestNextVisitViewSet, VisitViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"visits", VisitViewSet, basename="visits")
router.register(r"observations", ObservationViewSet, basename="observations")
router.register(
    r"suggest-next-visit", SuggestNextVisitViewSet, basename="suggest-next-visit"
)
