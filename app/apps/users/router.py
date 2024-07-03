from apps.users.views import UserListView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"users", UserListView, basename="users")
