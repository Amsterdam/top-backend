from apps.cases.views import CaseSearchViewSet, CaseViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"cases", CaseViewSet, basename="case")
router.register(r"search", CaseSearchViewSet, basename="search")
