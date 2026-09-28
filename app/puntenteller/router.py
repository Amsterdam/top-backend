from rest_framework.routers import DefaultRouter

from .views import PuntentellerViewSet

router = DefaultRouter()
router.register(r"puntenteller", PuntentellerViewSet, basename="puntenteller")
