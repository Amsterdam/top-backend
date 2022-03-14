from apps.addresses import router as addresses_router
from apps.cases import router as case_router
from apps.fraudprediction import router as fraudprediction_router
from apps.health.views import health_bwv, health_default
from apps.itinerary import router as itinerary_router
from apps.permits import router as permits_router
from apps.permits.views import DecosAPISearch
from apps.planner import router as planner_router
from apps.planner.views import dumpdata as planner_dumpdata
from apps.planner.views_sandbox import AlgorithmListView, AlgorithmView, BWVTablesView
from apps.users import router as users_router
from apps.users.views import IsAuthorizedView, ObtainAuthTokenOIDC
from apps.visits import router as visits_router
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

v1_urls = (
    itinerary_router.router.urls
    + fraudprediction_router.router.urls
    + case_router.router.urls
    + permits_router.router.urls
    + addresses_router.router.urls
    + planner_router.router.urls
    + users_router.router.urls
    + visits_router.router.urls
    + [
        path(
            "oidc-authenticate/",
            ObtainAuthTokenOIDC.as_view(),
            name="oidc-authenticate",
        ),
        path("is-authorized/", IsAuthorizedView.as_view(), name="is-authorized"),
    ]
)

urlpatterns = [
    # Admin environment
    path("admin/planner/dumpdata", planner_dumpdata, name="planner-dumpdata"),
    path("admin/decos-api-search/", DecosAPISearch.as_view(), name="decos_api_search"),
    path("admin/bwv-structure", BWVTablesView.as_view(), name="bwv-structure"),
    path("admin/", admin.site.urls),
    # Algorithm sandbox environment
    path("algorithm/", AlgorithmListView.as_view(), name="algorithm-list"),
    path("algorithm/<int:pk>", AlgorithmView.as_view(), name="algorithm-detail"),
    # Health check urls
    path("looplijsten/health", health_default, name="health-default"),
    path("looplijsten/health_bwv", health_bwv, name="health-bwv"),
    path("health/", include("health_check.urls")),
    # The API for requesting data
    path("api/v1/", include((v1_urls, "app"), namespace="v1")),
    path("api/v2/", include((v1_urls, "app"), namespace="v2")),
    # # Swagger/OpenAPI documentation
    path(
        "api/v1/schema/", SpectacularAPIView.as_view(api_version="v1"), name="schema-v1"
    ),
    path(
        "api/v1/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema-v1"),
        name="swagger-ui",
    ),
    path(
        "api/v2/schema/", SpectacularAPIView.as_view(api_version="v2"), name="schema-v2"
    ),
    path(
        "api/v2/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema-v2"),
        name="swagger-ui",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# JSON handlers for errors
handler500 = "rest_framework.exceptions.server_error"
handler400 = "rest_framework.exceptions.bad_request"
