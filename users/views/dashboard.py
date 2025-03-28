from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from users.authentication import JWTAuthentication
from users.models import UserModel
from albums.models import AlbumModel
from music.models import MusicModel
from django.db import connection

class UnifiedDashboardView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Returns comprehensive dashboard data based on user role.
        """
        user = getattr(request, 'user', None)

        if not user:
            raise AuthenticationFailed('User not authenticated or token invalid')

        role_type = getattr(user, 'role_type', None)

        # Base dashboard data
        dashboard_data = {
            "role": role_type,
            "user_info": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
            }
        }

        # Role-specific dashboard data
        if role_type == 'super_admin':
            dashboard_data.update(self.get_super_admin_dashboard())

        elif role_type == 'artist_manager':
            dashboard_data.update(self.get_artist_manager_dashboard())

        elif role_type == 'artist':
            dashboard_data.update(self.get_artist_dashboard(user))

        else:
            raise AuthenticationFailed('Invalid user role')

        return Response(dashboard_data)

    def get_super_admin_dashboard(self):
        """
        Generate dashboard data for super admin using raw SQL queries.
        """
        with connection.cursor() as cursor:
            # Get total users count
            cursor.execute("SELECT COUNT(id) FROM users")
            total_users = cursor.fetchone()[0]

            # Get total approved artists count
            cursor.execute("SELECT COUNT(id) FROM users WHERE role_type = 'artist' AND is_approved = 'true'")
            total_approved_artists = cursor.fetchone()[0]

            # Get total albums count
            cursor.execute("SELECT COUNT(id) FROM albums")
            total_albums = cursor.fetchone()[0]

            # Get total music tracks count
            cursor.execute("SELECT COUNT(music.id) FROM music")
            total_tracks = cursor.fetchone()[0]

            # Get users by role
            cursor.execute("SELECT role_type, COUNT(id) FROM users GROUP BY role_type")
            users_by_role = dict(cursor.fetchall())

        return {
            "total_users": total_users,
            "total_approved_artists": total_approved_artists,
            "system_overview": {
                "total_albums": total_albums,
                "total_tracks": total_tracks,
                "users_by_role": users_by_role,
            }
        }

    def get_artist_manager_dashboard(self):
        """
        Generate dashboard data for artist manager using raw SQL queries.
        """
        with connection.cursor() as cursor:
            # Get total artists count
            cursor.execute("SELECT COUNT(id) FROM users WHERE role_type = 'artist'")
            total_artists = cursor.fetchone()[0]

            # Get pending artist approvals count
            cursor.execute("SELECT COUNT(id) FROM users WHERE role_type = 'artist' AND status = 'pending'")
            pending_approvals = cursor.fetchone()[0]

            # Get total albums count
            cursor.execute("SELECT COUNT(id) FROM albums")
            total_albums = cursor.fetchone()[0]

            # Get total music tracks count
            cursor.execute("SELECT COUNT(id) FROM music")
            total_tracks = cursor.fetchone()[0]

        return {
            "total_artists": total_artists,
            "pending_approvals": pending_approvals,
            "managed_artists_overview": {
                "total_albums": total_albums,
                "total_tracks": total_tracks,
            }
        }

    def get_artist_dashboard(self, user):
        
        with connection.cursor() as cursor:
            # Get artist ID from artist table, not directly using user.id
            cursor.execute("""
                SELECT id FROM artist 
                WHERE user_id = %s
            """, [user.id])
            artist_result = cursor.fetchone()
            
            if not artist_result:
                return {
                    "total_works": 0,
                    "albums": [],
                    "music": [],
                    "dashboard_stats": {
                        "total_albums": 0,
                        "total_tracks": 0,
                    }
                }
            
            artist_id = artist_result[0]

            # Get total albums for the artist
            cursor.execute("SELECT COUNT(id) FROM albums WHERE artist_id = %s", [artist_id])
            total_albums = cursor.fetchone()[0]

            # Get albums data
            albums = AlbumModel.get_albums_by_artist(artist_id)

            # Get total tracks for the artist
            cursor.execute("""
                SELECT COUNT(m.id) 
                FROM music m
                JOIN albums a ON m.album_id = a.id
                WHERE a.artist_id = %s
            """, [artist_id])
            total_tracks = cursor.fetchone()[0]

            # Get music tracks data for the artist
            cursor.execute("""
                SELECT m.id, m.title, m.album_id, a.name as album_name
                FROM music m
                JOIN albums a ON m.album_id = a.id
                WHERE a.artist_id = %s
            """, [artist_id])
            columns = [col[0] for col in cursor.description]
            music = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return {
            "total_works": total_tracks,
            "albums": albums,
            "music": music,
            "dashboard_stats": {
                "total_albums": total_albums,
                "total_tracks": total_tracks,
            }
        }
