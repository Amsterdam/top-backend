from apps.permits.views import DecosViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"decos", DecosViewSet, basename="decos")
