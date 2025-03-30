from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import ArtistModel, AlbumModel, MusicModel
from .permissions import IsArtistOwner
from users.permissions import IsArtist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import UserModel
from django.db import connection
from users.authentication import JWTHandler
from users.permissions import IsArtistManager,IsSuperAdmin
import csv
from django.http import HttpResponse

class ArtistMusicView(APIView):
    permission_classes = [IsAuthenticated, IsArtistManager,IsSuperAdmin] 

    def get(self, request, artist_id):
        """
        Fetch all songs for a particular artist across all albums.
        """
        # Fetch albums associated with the artist
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id FROM albums
                WHERE artist_id = %s
            """, [artist_id])
            
            albums = cursor.fetchall()
            
            if not albums:
                return Response({"error": "No albums found for this artist"}, status=status.HTTP_404_NOT_FOUND)

            # Get songs for each album
            songs = []
            for album in albums:
                album_id = album[0]
                cursor.execute("""
                    SELECT id, title, genre, duration, track_number, release_date, cover_page 
                    FROM music
                    WHERE album_id = %s
                    ORDER BY track_number
                """, [album_id])
                album_songs = cursor.fetchall()
                for song in album_songs:
                    songs.append({
                        "id": song[0],  # Song ID
                        "title": song[1],  # Song Title
                        "genre": song[2],  # Song Genre
                        "duration": str(song[3]),  # Song Duration as string
                        "track_number": song[4],  # Track Number
                        "release_date": song[5],  # Release Date
                        "cover_page": song[6],  # Cover Image URL or Path
                    })

        return Response(songs, status=status.HTTP_200_OK)
class ArtistLoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        # Authenticate user
        user = UserModel.authenticate_user(email, password)
        
        if not user:
            return Response(
                {"detail": "Invalid credentials or not an approved artist"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Generate tokens
        access_token, refresh_token = JWTHandler.generate_tokens(user['id'])
        
        return Response({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': user['id'],
            'artist_id': user.get('artist_id'),
            'role': 'artist'
        })

class ArtistProfileView(APIView):
    permission_classes = [IsAuthenticated, IsArtist]

    def get(self, request):
        """
        Get artist's profile
        """
        artist = ArtistModel.get_artist_by_user_id(request.user.id)
        if not artist:
            return Response({"error": "Artist profile not found"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(artist, status=status.HTTP_200_OK)

    def put(self, request):
        """
        Update artist profile
        """
        # Fetch the artist profile by the user ID
        artist = ArtistModel.get_artist_by_user_id(request.user.id)
        
        if not artist:
            return Response({"error": "Artist profile not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Get the data from the request (exclude first_release_year since it's removed)
        update_data = {
            'name': request.data.get('name'), 
            'bio': request.data.get('bio'),
            'nationality': request.data.get('nationality'),
            'photo_url': request.data.get('photo_url')
        }

        # Remove None values from the data dictionary (optional fields will not be updated)
        update_data = {k: v for k, v in update_data.items() if v is not None}

        # Call the update method from the model to update the artist profile
        if ArtistModel.update_artist_profile(artist['id'], **update_data):
            return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)
        
        return Response({"error": "Update failed"}, status=status.HTTP_400_BAD_REQUEST)


class AlbumView(APIView):
    permission_classes = [IsAuthenticated, IsArtistOwner]

    def post(self, request):
        """
        Create a new album
        """
        artist = ArtistModel.get_artist_by_user_id(request.user.id)
        
        album_data = {
            'name': request.data.get('name'),
            'release_year': request.data.get('release_year'),
            'photo_url': request.data.get('photo_url')
        }
        
        album_id = AlbumModel.create_album(
            artist_id=artist['id'], 
            **album_data
        )
        
        return Response({
            "message": "Album created successfully",
            "album_id": album_id
        }, status=status.HTTP_201_CREATED)

    def get(self, request):
        """
        Get all albums for the artist
        """
        artist = ArtistModel.get_artist_by_user_id(request.user.id)
        albums = AlbumModel.get_artist_albums(artist['id'])
        
        return Response(albums, status=status.HTTP_200_OK)


class MusicView(APIView):
    permission_classes = [IsAuthenticated, IsArtistOwner]

    def post(self, request):
        """
        Add a track to an album
        """
        artist = ArtistModel.get_artist_by_user_id(request.user.id)
        
        track_data = {
            'album_id': request.data.get('album_id'),
            'title': request.data.get('title'),
            'genre': request.data.get('genre')
        }
        
        track_id = MusicModel.create_track(
            artist_id=artist['id'], 
            **track_data
        )
        
        return Response({
            "message": "Track added successfully",
            "track_id": track_id
        }, status=status.HTTP_201_CREATED)

    def get(self, request):
        """
        Get tracks for a specific album
        """
        album_id = request.query_params.get('album_id')
        if not album_id:
            return Response({"error": "Album ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        tracks = MusicModel.get_album_tracks(album_id)
        return Response(tracks, status=status.HTTP_200_OK)
    # 🚀 CSV EXPORT ARTISTS
class ExportArtistsCSVView(APIView):
    permission_classes = [IsAuthenticated, IsArtistManager]

    def get(self, request):
        """
        Export all artists as a CSV file.
        """
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="artists.csv"'

        writer = csv.writer(response)
        writer.writerow(["ID", "Name", "Bio", "Nationality"])

        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name, bio, nationality FROM artist_model")
            artists = cursor.fetchall()

        for artist in artists:
            writer.writerow(artist)

        return response
# 🚀 CSV IMPORT ARTISTS
class ImportArtistsCSVView(APIView):
    permission_classes = [IsAuthenticated, IsArtistManager]

    def post(self, request):
        """
        Import artists from a CSV file.
        """
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "CSV file is required"}, status=status.HTTP_400_BAD_REQUEST)

        decoded_file = file.read().decode("utf-8").splitlines()
        reader = csv.reader(decoded_file)
        next(reader)  # Skip header row

        with connection.cursor() as cursor:
            for row in reader:
                cursor.execute(
                    "INSERT INTO artist_model (name, bio, nationality) VALUES (%s, %s, %s)",
                    (row[0], row[1], row[2]),
                )

        return Response({"message": "Artists imported successfully"}, status=status.HTTP_201_CREATED)

