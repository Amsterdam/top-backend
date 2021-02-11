from apps.cases.views import CaseSearchViewSet, CaseViewSet, PermitViewSet
from apps.fraudprediction.views import FraudPredictionScoringViewSet
from apps.health.views import health_bwv, health_default
from apps.itinerary.views import ItineraryItemViewSet, ItineraryViewSet, NoteViewSet
from apps.permits.views import DecosAPISearch, DecosViewSet
from apps.planner.views import (
    DaySettingsViewSet,
    PostalCodeRangePresetViewSet,
    TeamSettingsViewSet,
)
from apps.planner.views import dumpdata as planner_dumpdata
from apps.planner.views_sandbox import AlgorithmListView, AlgorithmView, BWVTablesView
from apps.users.views import IsAuthorizedView, ObtainAuthTokenOIDC, UserListView
from apps.visits.views import ObservationViewSet, SuggestNextVisitViewSet, VisitViewSet
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
api_router.register(r"decos", DecosViewSet, basename="decos")
api_router.register(r"users", UserListView, basename="users")
api_router.register(r"visits", VisitViewSet, basename="visits")
api_router.register(r"observations", ObservationViewSet, basename="observations")
api_router.register(
    r"suggest-next-visit", SuggestNextVisitViewSet, basename="suggest-next-visit"
)

api_router.register(r"team-settings", TeamSettingsViewSet, basename="team-settings")
api_router.register(r"day-settings", DaySettingsViewSet, basename="day-settings")
api_router.register(
    r"postal-code-ranges-presets",
    PostalCodeRangePresetViewSet,
    basename="postal-code-ranges-presets",
)
api_router.register(
    r"fraud-prediction/scoring",
    FraudPredictionScoringViewSet,
    basename="fraud-prediction-score",
)

urlpatterns = [
    # Admin environment
    path("admin/", admin.site.urls),
    path("admin/planner/dumpdata", planner_dumpdata, name="planner-dumpdata"),
    # Algorithm sandbox environment
    path("admin/bwv-structure", BWVTablesView.as_view(), name="bwv-structure"),
    path("algorithm/", AlgorithmListView.as_view(), name="algorithm-list"),
    path("algorithm/<int:pk>", AlgorithmView.as_view(), name="algorithm-detail"),
    # Health check urls
    path("looplijsten/health", health_default, name="health-default"),
    path("looplijsten/health_bwv", health_bwv, name="health-bwv"),
    path("health/", include("health_check.urls")),
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
        "api/v1/is-authorized/",
        IsAuthorizedView.as_view(),
        name="is-authorized",
    ),
    # # Swagger/OpenAPI documentation
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/v1/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("admin/decos-api-search/", DecosAPISearch.as_view(), name="decos_api_search"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# JSON handlers for errors
handler500 = "rest_framework.exceptions.server_error"
handler400 = "rest_framework.exceptions.bad_request"
