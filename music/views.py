from django.db import connection
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.permissions import IsArtist
from .models import MusicModel
from .serializers import MusicSerializer

class MusicViewSet(APIView):
    permission_classes = [IsArtist]

    def get(self, request, album_id, music_id=None):
        artist = self.get_artist_from_user(request.user.id)

        if not self.verify_album_ownership(album_id, artist['id']):
            return Response({"detail": "Album not found"}, status=404)

        if music_id:
            music = [m for m in MusicModel.get_music_by_album(album_id) if m["id"] == music_id]
            if not music:
                return Response({"detail": "Music not found"}, status=404)
            return Response(music[0])
        
        music = MusicModel.get_music_by_album(album_id)
        return Response(music)

    def post(self, request, album_id):
        # Get the current artist's ID
        artist = self.get_artist_from_user(request.user.id)
        
        # Verify album belongs to artist
        if not self.verify_album_ownership(album_id, artist['id']):
            return Response(
                {"detail": "Album not found or you don't have permission"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validate incoming data
        serializer = MusicSerializer(data={
            **request.data,
            'album_id': album_id
        })
        
        if serializer.is_valid():
            music = MusicModel.create_music(serializer.validated_data)
            return Response(music, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, album_id, music_id):
        artist = self.get_artist_from_user(request.user.id)

        if not self.verify_album_ownership(album_id, artist['id']):
            return Response({"detail": "Album not found or you don't have permission"}, status=404)

        serializer = MusicSerializer(data=request.data, partial=True)

        if serializer.is_valid():
            music = MusicModel.update_music(music_id, album_id, serializer.validated_data)
            if music:
                return Response(music)
            else:
                return Response({"detail": "Music not found"}, status=404)

        return Response(serializer.errors, status=400)

    def delete(self, request, album_id, music_id):
        artist = self.get_artist_from_user(request.user.id)

        if not self.verify_album_ownership(album_id, artist['id']):
            return Response({"detail": "Album not found or you don't have permission"}, status=404)

        success = MusicModel.delete_music(music_id, album_id)

        if success:
            return Response(status=204)
        else:
            return Response({"detail": "Music not found"}, status=404)

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

    def verify_album_ownership(self, album_id, artist_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 1 FROM albums 
                WHERE id = %s AND artist_id = %s
            """, [album_id, artist_id])
            result = cursor.fetchone()
            print(f"Debug - Ownership check: {result is not None}")  # Debug line
            return result is not None
