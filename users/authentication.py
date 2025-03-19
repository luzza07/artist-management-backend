# authentication.py
import jwt
import os
import datetime
from django.conf import settings
from django.db import connection
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from .models import UserModel

SECRET_KEY = os.getenv('SECRET_KEY')

class JWTHandler:
    @staticmethod
    def generate_tokens(user_id):
        access_token_exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        refresh_token_exp = datetime.datetime.utcnow() + datetime.timedelta(days=7)

        access_token = jwt.encode(
            {"user_id": user_id, "exp": access_token_exp},
            SECRET_KEY,
            algorithm="HS256"
        )

        refresh_token = jwt.encode(
            {"user_id": user_id, "exp": refresh_token_exp},
            SECRET_KEY,
            algorithm="HS256"
        )

        return access_token, refresh_token

    @staticmethod
    def decode_token(token):
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return decoded
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None
            
        token = auth_header.split(' ')[1]
        if not token:
            return None
            
        payload = JWTHandler.decode_token(token)
        if payload is None:
            raise exceptions.AuthenticationFailed('Invalid token or token expired')
            
        user_id = payload.get('user_id')
        user = UserModel.get_user_by_id(user_id)
        
        if not user:
            raise exceptions.AuthenticationFailed('User not found')
            
        if not user['is_approved']:
            raise exceptions.AuthenticationFailed('User not approved')
            
        return (user, token)
        
    def authenticate_header(self, request):
        return 'Bearer'