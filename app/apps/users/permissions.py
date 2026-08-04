from rest_framework.permissions import SAFE_METHODS, BasePermission


class InAuthGroup(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsInAuthorizedRealm(InAuthGroup):
    """
    Keep for backwards compatibility
    """


class CanManageSettingsOrReadOnly(InAuthGroup):
    permission = "planner.manage_settings"

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        # Read access is allowed for all authenticated users, but require the manage_settings permission for write access
        return request.method in SAFE_METHODS or request.user.has_perm(self.permission)
