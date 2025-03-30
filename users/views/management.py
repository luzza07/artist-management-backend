
from django.contrib.auth.hashers import make_password
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
from users.permissions import IsSuperAdmin
from users.models import UserModel
from albums.models import AlbumModel
from music.models import MusicModel
from users.authentication import JWTHandler 
from users.serializers import UserSignupSerializer
from rest_framework.pagination import PageNumberPagination

class UserPagination(PageNumberPagination):
    page_size = 10  # Number of users per page
    page_size_query_param = "page_size"
    max_page_size = 100
    
class CreateUserView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request):
        """
        Handles user signup.
        Automatically approves artists and creates approval requests for super_admins and artist_managers.
        """
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            hashed_password = make_password(data["password"])

            # Automatically approve artists
            is_approved = data["role_type"] == "artist"

            try:
                # Create user
                user_id = UserModel.create_user(
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                    email=data["email"],
                    password=hashed_password,
                    phone=data.get("phone"),
                    dob=data.get("dob"),
                    gender=data["gender"],
                    address=data.get("address"),
                    role_type=data["role_type"],
                    is_approved=is_approved
                )

                response_data = {
                    "message": "User created successfully.",
                    "user_id": user_id,
                    "is_approved": is_approved
                }

                # Generate tokens for auto-approved users (artists)
                if is_approved:
                    access_token, refresh_token = JWTHandler.generate_tokens(user_id)
                    response_data["access_token"] = access_token
                    response_data["refresh_token"] = refresh_token
                else:
                    response_data["message"] += " Pending approval by a super admin."

                return Response(response_data, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListUsersView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        """
        Super Admin can list all users via raw SQL, with column names.
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, first_name, last_name, email, role_type, is_approved FROM users WHERE is_approved = TRUE
            """)
            rows = cursor.fetchall()

        # Define column headers
        columns = ['id', 'first_name', 'last_name', 'email', 'role_type', 'is_approved']
        
        # Format the response with column names
        formatted_users = [dict(zip(columns, row)) for row in rows]

        return Response({"users": formatted_users}, status=status.HTTP_200_OK)


class UpdateUserView(APIView):
    permission_classes = [IsSuperAdmin]

    def put(self, request, user_id):
        """
        Super Admin can update users via raw SQL, and password is hashed before being updated.
        """
        data = request.data
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        password = data.get("password")  # This will be hashed if provided
        
        # Hash the password if it's provided
        if password:
            hashed_password = make_password(password)
        else:
            # If no password is provided, do not update the password field
            hashed_password = None

        with connection.cursor() as cursor:
            # Only update the password if it's been hashed
            if hashed_password:
                cursor.execute("""
                    UPDATE users
                    SET first_name = %s, last_name = %s, email = %s, password = %s
                    WHERE id = %s
                """, [first_name, last_name, email, hashed_password, user_id])
            else:
                cursor.execute("""
                    UPDATE users
                    SET first_name = %s, last_name = %s, email = %s, role_type = %s, is_approved = %s
                    WHERE id = %s
                """, [first_name, last_name, email,  user_id])

        return Response({"message": "User updated successfully."}, status=status.HTTP_200_OK)

class DeleteUserView(APIView):
    permission_classes = [IsSuperAdmin]

    def delete(self, request, user_id):
        """
        Super Admin can delete a user via raw SQL.
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM users WHERE id = %s
            """, [user_id])

        return Response({"message": "User deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class CreateArtistView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request):
        """
        Handles user signup.
        Automatically approves artists and creates approval requests for super_admins and artist_managers.
        """
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            hashed_password = make_password(data["password"])

            # Automatically approve artists
            is_approved = data["role_type"] == "artist"

            try:
                # Create user
                user_id = UserModel.create_user(
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                    email=data["email"],
                    password=hashed_password,
                    phone=data.get("phone"),
                    dob=data.get("dob"),
                    gender=data["gender"],
                    address=data.get("address"),
                    role_type=data["role_type"],
                    is_approved=is_approved
                )

                response_data = {
                    "message": "User created successfully.",
                    "user_id": user_id,
                    "is_approved": is_approved
                }

                # Generate tokens for auto-approved users (artists)
                if is_approved:
                    access_token, refresh_token = JWTHandler.generate_tokens(user_id)
                    response_data["access_token"] = access_token
                    response_data["refresh_token"] = refresh_token
                else:
                    response_data["message"] += " Pending approval by a super admin."

                return Response(response_data, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListArtistsView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        """
        Super Admin can list all artists via raw SQL, with column names.
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM artist
            """)
            rows = cursor.fetchall()

        # Define column headers
        columns = ['id', 'user_id', 'name','bio','nationality','no_of_albums_released','no_of_songs']
        
        # Format the response with column names
        formatted_artists = [dict(zip(columns, row)) for row in rows]

        return Response({"artists": formatted_artists}, status=status.HTTP_200_OK)


class UpdateArtistView(APIView):
    permission_classes = [IsSuperAdmin]

    def put(self, request, artist_id):
        """
        Super Admin can update an artist via raw SQL.
        """
        data = request.data
        artist_name = data.get("artist_name")
        genre = data.get("genre")

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE artist
                SET artist_name = %s, genre = %s
                WHERE id = %s
            """, [artist_name, genre, artist_id])

        return Response({"message": "Artist updated successfully."}, status=status.HTTP_200_OK)

class DeleteArtistView(APIView):
    permission_classes = [IsSuperAdmin]

    def delete(self, request, artist_id):
        """
        Super Admin can delete an artist via raw SQL.
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM artist WHERE id = %s
            """, [artist_id])

        return Response({"message": "Artist deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
