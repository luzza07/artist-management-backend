from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from users.authentication import JWTAuthentication
from users.models import UserModel

class SuperAdminDashboardView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  # Ensures user is authenticated

    def get(self, request):
        """
        Returns dashboard data for the Super Admin role.
        """
        # Ensure user is available in request
        user = getattr(request, 'user', None)
        
        if not user:
            raise AuthenticationFailed('User not authenticated or token invalid')
        
        # Debug information
        print(f"User attributes: {vars(user)}")
        
        role_type = getattr(user, 'role_type', None)
        print(f"Role type: {role_type}")
        
        # Check for 'super_admin' (with underscore) not 'super-admin' (with hyphen)
        if not role_type or role_type != 'super_admin':
            raise AttributeError('User role type is missing or invalid')

        # Use raw SQL methods
        total_users = UserModel.get_total_users_count()
        total_approved_artists = UserModel.get_approved_artists_count()
        
        data = {
            "message": "Welcome, Super Admin!",
            "total_users": total_users,
            "total_approved_artists": total_approved_artists,
        }

        return Response(data)

class ArtistManagerDashboardView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Returns dashboard data for the Artist Manager role.
        """
        user = getattr(request, 'user', None)
        
        if not user:
            raise AuthenticationFailed('User not authenticated or token invalid')

        role_type = getattr(user, 'role_type', None)
        # Check for 'artist_manager' (with underscore) not 'artist-manager' (with hyphen)
        if not role_type or role_type != 'artist_manager':
            raise AttributeError('User role type is missing or invalid')

        # Use raw SQL methods
        total_artists = UserModel.get_artists_count()
        pending_approvals = UserModel.get_pending_artists_count()

        data = {
            "message": "Welcome, Artist Manager!",
            "total_artists": total_artists,
            "pending_approvals": pending_approvals,
        }

        return Response(data)


class ArtistDashboardView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Returns dashboard data for the Artist role.
        """
        user = getattr(request, 'user', None)
        
        if not user:
            raise AuthenticationFailed('User not authenticated or token invalid')

        role_type = getattr(user, 'role_type', None)
        if not role_type or role_type != 'artist':
            raise AttributeError('User role type is missing or invalid')

        # Use raw SQL for artist works
        artist_works = UserModel.get_artist_works(user.id)
        
        data = {
            "message": "Welcome, Artist!",
            "total_works": len(artist_works),
            "recent_works": [work['title'] for work in artist_works[:5]] if artist_works else [],
        }

        return Response(data)