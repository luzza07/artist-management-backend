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
from users.authentication import JWTHandler

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