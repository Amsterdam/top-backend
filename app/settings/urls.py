from apps.addresses import router as addresses_router
from apps.cases import router as case_router
from apps.health.views import health_default, is_healthy
from apps.itinerary import router as itinerary_router
from apps.planner import router as planner_router
from apps.planner.views import dumpdata as planner_dumpdata
from apps.users import router as users_router
from apps.users.views import IsAuthorizedView, ObtainAuthTokenOIDC
from apps.visits import router as visits_router
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path, re_path
from django.views.generic import View
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


class MyView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({}, status=204)


admin.site.site_header = "Wonen looplijsten"
admin.site.site_title = "Wonen looplijsten"
admin.site.index_title = "Wonen looplijsten"

v1_urls = (
    itinerary_router.router.urls
    + case_router.router.urls
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
    path("admin/", admin.site.urls),
    # Health check urls
    path("looplijsten/health", health_default, name="health-default"),
    path("health/", include("health_check.urls")),
    path("startup", is_healthy),
    # The API for requesting data
    path("api/v1/", include((v1_urls, "app"), namespace="v1")),
    re_path(r"^$", view=MyView.as_view(), name="index"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [
        # # Swagger/OpenAPI documentation
        path(
            "api/v1/schema/",
            SpectacularAPIView.as_view(api_version="v1"),
            name="schema-v1",
        ),
        path(
            "api/v1/swagger/",
            SpectacularSwaggerView.as_view(url_name="schema-v1"),
            name="swagger-ui",
        ),
    ]

# JSON handlers for errors
handler500 = "rest_framework.exceptions.server_error"
handler400 = "rest_framework.exceptions.bad_request"
