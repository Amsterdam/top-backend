from apps.cases.views import CaseSearchViewSet, CaseViewSet, PermitViewSet
from apps.fraudprediction.views import FraudPredictionScoringViewSet
from apps.health.views import health_bwv, health_default
from apps.itinerary.views import ItineraryItemViewSet, ItineraryViewSet, NoteViewSet
from apps.planner.views import (
    ConstantsProjectsViewSet,
    ConstantsStadiaViewSet,
    SettingsPlannerViewSet,
    TeamSettingsViewSet,
)
from apps.planner.views_sandbox import AlgorithmView
from apps.users.views import IsAuthenticatedView, ObtainAuthTokenOIDC, UserListView
from apps.visits.views import VisitViewSet
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

admin.site.site_header = "Wonen looplijsten"
admin.site.site_title = "Wonen looplijsten"
admin.site.index_title = "Wonen looplijsten"

api_router = DefaultRouter()
api_router.register(r"itineraries", ItineraryViewSet, basename="itinerary")
api_router.register(r"itinerary-items", ItineraryItemViewSet, basename="itinerary-item")
api_router.register(r"cases", CaseViewSet, basename="case")
api_router.register(r"search", CaseSearchViewSet, basename="search")
api_router.register(r"notes", NoteViewSet, basename="notes")
api_router.register(r"permits", PermitViewSet, basename="permits")
api_router.register(r"users", UserListView, basename="users")
api_router.register(r"visits", VisitViewSet, basename="visits")
api_router.register(
    r"constants/projects", ConstantsProjectsViewSet, basename="constants-projects"
)
api_router.register(
    r"constants/stadia", ConstantsStadiaViewSet, basename="constants-stadia"
)
api_router.register(
    r"settings/planner", SettingsPlannerViewSet, basename="settings-planner"
)
api_router.register(r"team-settings", TeamSettingsViewSet, basename="team-settings")
api_router.register(
    r"fraud-prediction/scoring",
    FraudPredictionScoringViewSet,
    basename="fraud-prediction-score",
)

urlpatterns = [
    # Admin environment
    path("admin/", admin.site.urls),
    # Algorithm sandbox environment
    path("algorithm/", AlgorithmView.as_view(), name="algorithm"),
    # Health check urls
    path("looplijsten/health", health_default, name="health-default"),
    path("looplijsten/health_bwv", health_bwv, name="health-bwv"),
    # The API for requesting data
    path("api/v1/", include(api_router.urls), name="api"),
    # Authentication endpoint for exchanging an OIDC code for a token
    path(
        "api/v1/oidc-authenticate/",
        ObtainAuthTokenOIDC.as_view(),
        name="oidc-authenticate",
    ),
    # Endpoint for checking if user is authenticated
    path(
        "api/v1/is-authenticated/",
        IsAuthenticatedView.as_view(),
        name="is-authenticated",
    ),
    # # Swagger/OpenAPI documentation
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/v1/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# JSON handlers for errors
handler500 = "rest_framework.exceptions.server_error"
handler400 = "rest_framework.exceptions.bad_request"
