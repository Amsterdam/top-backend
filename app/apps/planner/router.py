from apps.planner.views import DaySettingsViewSet, TeamSettingsViewSet, TeamSettingsThemesViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"team-settings", TeamSettingsViewSet, basename="team-settings")
router.register(r"day-settings", DaySettingsViewSet, basename="day-settings")
router.register(r"themes", TeamSettingsThemesViewSet, basename="themes")
