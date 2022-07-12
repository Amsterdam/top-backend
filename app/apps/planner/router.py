from apps.planner.views import DaySettingsViewSet, TeamSettingsViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"team-settings", TeamSettingsViewSet, basename="team-settings")
router.register(r"day-settings", DaySettingsViewSet, basename="day-settings")
