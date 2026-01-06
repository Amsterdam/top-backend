from apps.cases.views import CaseSearchV2ViewSet, CaseSearchViewSet, CaseViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"cases", CaseViewSet, basename="case")
router.register(r"search", CaseSearchViewSet, basename="search")
router.register(
    r"search-v2",
    CaseSearchV2ViewSet,
    basename="search-v2",
)
