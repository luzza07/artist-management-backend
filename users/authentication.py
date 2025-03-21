import jwt
import os
import datetime
from django.conf import settings
from django.db import connection
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from .models import UserModel

SECRET_KEY = os.getenv('SECRET_KEY')

# Updated User class to properly handle attributes
class User:
    def __init__(self, **kwargs):
        # Explicitly set role_type from kwargs or default to None
        self.role_type = kwargs.get('role_type', None)
        
        # Now set all other attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
            
        # Set authentication properties needed by DRF
        self.is_authenticated = True
        self.is_active = kwargs.get('is_approved', False)
    
    def __str__(self):
        return self.email if hasattr(self, 'email') else str(self.id)
        
    @property
    def is_superuser(self):
        return self.role_type == 'super_admin'

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
        user_dict = UserModel.get_user_by_id(user_id)  # Using your raw SQL method
        
        if not user_dict:
            raise exceptions.AuthenticationFailed('User not found')
            
        if not user_dict.get('is_approved', False):
            raise exceptions.AuthenticationFailed('User not approved')
            
        # Convert the dictionary to a User object
        user = User(**user_dict)
            
        return (user, token)  # Now returning a User object with necessary properties
        
    def authenticate_header(self, request):
        return 'Bearer'