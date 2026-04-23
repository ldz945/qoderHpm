from django.conf import settings
from rest_framework.permissions import BasePermission


class HpmActionPermission(BasePermission):
    """Action-level permission checker controlled by view.required_permissions."""

    message = 'You do not have permission to perform this action.'

    def has_permission(self, request, view):
        if hasattr(view, 'get_required_permissions'):
            required = view.get_required_permissions(request)
        else:
            required_map = getattr(view, 'required_permissions', None)
            if not required_map:
                return True
            action = getattr(view, 'action', None)
            required = required_map.get(action) or required_map.get('*') or []

        if not required:
            return True

        # Keep current dev flow unchanged until enforcement is turned on.
        if not getattr(settings, 'HPM_PERMISSION_ENFORCEMENT', False):
            return True

        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True

        return user.has_perms(required)
