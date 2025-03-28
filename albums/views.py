from .serializers import AlbumSerializer
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.permissions import IsArtist
from .models import AlbumModel
from django.http import Http404

class AlbumViewSet(APIView):
    permission_classes = [IsArtist]

    def get(self, request, album_id=None):  # Make album_id optional
        artist = self.get_artist_from_user(request.user.id)
        
        if album_id is None:
            # List all albums
            albums = AlbumModel.get_albums_by_artist(artist['id'])
            return Response(albums)
        else:
            # Get single album
            album = self.get_album_or_404(album_id, artist['id'])
            return Response(album)

    def get_album_or_404(self, album_id, artist_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, artist_id, name, release_year, genre, photo_url, tracklist, total_tracks, total_duration, created_at, updated_at
                FROM albums
                WHERE id = %s AND artist_id = %s
            """, [album_id, artist_id])
            result = cursor.fetchone()
            if not result:
                raise Http404("Album not found")
            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, result))

    def post(self, request):
        # Get the current artist's ID
        artist = self.get_artist_from_user(request.user.id)
        
        # Validate incoming data
        serializer = AlbumSerializer(data={
            **request.data,
            'artist_id': artist['id']
        })
        
        if serializer.is_valid():
            album = AlbumModel.create_album(artist['id'], serializer.validated_data)
            return Response(album, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, album_id):
        # Get the current artist's ID
        artist = self.get_artist_from_user(request.user.id)
        
        # Validate incoming data
        serializer = AlbumSerializer(data={
            **request.data,
            'artist_id': artist['id']
        }, partial=True)
        
        if serializer.is_valid():
            album = AlbumModel.update_album(album_id, artist['id'], serializer.validated_data)
            
            if album:
                return Response(album)
            else:
                return Response(
                    {"detail": "Album not found or you don't have permission"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, album_id):
        # Get the current artist's ID
        artist = self.get_artist_from_user(request.user.id)
        
        success = AlbumModel.delete_album(album_id, artist['id'])
        
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"detail": "Album not found or you don't have permission"},
                status=status.HTTP_404_NOT_FOUND
            )

    def get_artist_from_user(self, user_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, user_id 
                FROM artist 
                WHERE user_id = %s
            """, [user_id])
            result = cursor.fetchone()
            if not result:
                raise Exception("Artist profile not found")
            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, result))
