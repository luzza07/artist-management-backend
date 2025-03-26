
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import UserModel
from users.serializers import UserSignupSerializer, UserLoginSerializer
from users.authentication import JWTHandler

class SignupView(APIView):
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


class LoginView(APIView):
    def post(self, request):
        """
        Handles user login.
        Only allows login for approved users.
        """
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = UserModel.get_user_by_email(data["email"])

            if user and check_password(data["password"], user["password"]):
                if not user["is_approved"]:
                    return Response({"error": "Your account is pending approval."}, status=status.HTTP_403_FORBIDDEN)

                # Generate tokens for approved users
                access_token, refresh_token = JWTHandler.generate_tokens(user["id"])
                return Response({
                    "message": "Login successful",
                    "user": {
                        "id": user["id"],
                        "email": user["email"],
                        "first_name": user["first_name"],
                        "last_name": user["last_name"],
                        "role_type": user["role_type"]
                    },
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class RefreshTokenView(APIView):
    """
    Handles token refresh using a valid refresh token.
    """
    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Decode the refresh token
        payload = JWTHandler.decode_token(refresh_token)
        if not payload:
            return Response({"error": "Invalid or expired refresh token."}, status=status.HTTP_401_UNAUTHORIZED)

        # Fetch the user
        user_id = payload.get("user_id")
        user = UserModel.get_user_by_id(user_id)
        if not user or not user["is_approved"]:
            return Response({"error": "User not found or not approved."}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate new tokens
        access_token, new_refresh_token = JWTHandler.generate_tokens(user_id)
        return Response({
            "access_token": access_token,
            "refresh_token": new_refresh_token
        })