from apps.permits.views import DecosViewSet, PermitViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"decos", DecosViewSet, basename="decos")
router.register(r"addresses", PermitViewSet, basename="addresses")
