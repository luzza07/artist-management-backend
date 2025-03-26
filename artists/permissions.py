from rest_framework.permissions import BasePermission
from users.models import UserModel
from artists.models import ArtistModel

class IsArtistOwner(BasePermission):
    """
    Custom permission to only allow artists to manage their own resources
    """
    def has_permission(self, request, view):
        # Only allow authenticated artists
        return request.user.role_type == 'artist'

    def has_object_permission(self, request, view, obj):
        # Get the artist associated with the current user
        artist = ArtistModel.get_artist_by_user_id(request.user.id)
        
        # Check object ownership based on view type
        if view.__class__.__name__ == 'AlbumViewSet':
            return obj['artist_id'] == artist['id']
        elif view.__class__.__name__ == 'MusicViewSet':
            return obj['artist_id'] == artist['id']
        
        return False