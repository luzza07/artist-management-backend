from django.contrib.auth.hashers import make_password, check_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserModel
from .serializers import UserSignupSerializer, UserLoginSerializer
from .authentication import JWTHandler

class SignupView(APIView):
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            hashed_password = make_password(data["password"])

            user_id = UserModel.create_user(
                data["first_name"], data["last_name"], data["email"], hashed_password,
                data.get("phone"), data.get("dob"), data["gender"], data.get("address"), data["role_type"]
            )

            return Response({"message": "User created successfully", "user_id": user_id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = UserModel.get_user_by_email(data["email"])

            if user and check_password(data["password"], user[4]):  # user[4] is password
                access_token, refresh_token = JWTHandler.generate_tokens(user[0])  # user[0] is id
                return Response({"access_token": access_token, "refresh_token": refresh_token}, status=status.HTTP_200_OK)

        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
