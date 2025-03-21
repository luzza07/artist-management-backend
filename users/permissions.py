from rest_framework.permissions import BasePermission
from users.models import UserModel  # Importing your raw SQL model

class IsSuperAdmin(BasePermission):
    """
    Allows access only to Super Admins.
    """
    def has_permission(self, request, view):
        user = request.user
        return user and user.get("role_type") == "super_admin"

class IsArtistManager(BasePermission):
    """
    Allows access only to Artist Managers.
    """
    def has_permission(self, request, view):
        user = request.user
        return user and user.get("role_type") == "artist_manager"

class IsArtist(BasePermission):
    """
    Allows access only to Artists.
    """
    def has_permission(self, request, view):
        user = request.user
        return user and user.get("role_type") == "artist"

class IsApprovedUser(BasePermission):
    """
    Allows access only to approved users (any role).
    """
    def has_permission(self, request, view):
        user = request.user
        return user and user.get("is_approved") is True
