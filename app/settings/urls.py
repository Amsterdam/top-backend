import os

from apps.addresses import router as addresses_router
from apps.cases import router as case_router
from apps.health.views import health_default, is_healthy
from apps.itinerary import router as itinerary_router
from apps.planner import router as planner_router
from apps.planner.views import dumpdata
from apps.users import router as users_router
from apps.users.views import IsAuthorizedView, ObtainAuthTokenOIDC
from apps.visits import router as visits_router
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import include, path, re_path
from django.views.generic import RedirectView, View
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


@login_required
def admin_redirect(request):
    return redirect("/admin")


class MyView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({}, status=204)


admin.site.site_header = "Toezicht op pad"
admin.site.site_title = "TOP Admin"
admin.site.index_title = os.getenv("ENVIRONMENT", "").upper()

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
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("admin/login/", admin_redirect),
    path(
        "admin/planner/dumpdata/",
        admin.site.admin_view(dumpdata),
        name="planner-dumpdata",
    ),
    path("admin/", admin.site.urls),
    # Health check urls
    path("looplijsten/health", health_default, name="health-default"),
    path("health/", include("health_check.urls")),
    path("startup", is_healthy),
    # The API for requesting data
    path("api/v1/", include((v1_urls, "app"), namespace="v1")),
    path(
        "favicon.ico", RedirectView.as_view(url="/static/favicon.ico", permanent=True)
    ),
    path(
        ".well-known/security.txt",
        RedirectView.as_view(url="https://www.amsterdam.nl/.well-known/security.txt"),
    ),
    re_path(r"^$", view=MyView.as_view(), name="index"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG or os.getenv("ENVIRONMENT", "").lower() == "acceptance":
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
