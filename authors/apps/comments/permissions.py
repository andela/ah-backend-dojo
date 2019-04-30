from rest_framework import permissions
from ..profiles.models import Profile


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Customize permission to only allow the owner of the comment to update or delete it"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == Profile.objects.get(user=request.user)
