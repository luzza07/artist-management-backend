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
    @classmethod
    def authenticate_user(cls, email, password):
        # Hash the password (ensure this matches your hashing method)
        hashed_password = cls.hash_password(password)
        
        try:
            with connection.cursor() as cursor:
                # Check user credentials and verify they are an artist
                cursor.execute("""
                    SELECT u.*, a.id AS artist_id 
                    FROM users u
                    LEFT JOIN artist a ON a.user_id = u.id
                    WHERE u.email = %s 
                    AND u.password = %s 
                    AND u.role_type = 'artist'
                    AND u.is_approved = TRUE
                """, [email, hashed_password])
                
                user = cursor.fetchone()
                
                if user:
                    # Convert to dictionary
                    columns = [col[0] for col in cursor.description]
                    return dict(zip(columns, user))
                
                return None
        
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    @staticmethod
    def hash_password(password):
        # Use SHA-256 for password hashing (replace with more secure method in production)
        return hashlib.sha256(password.encode()).hexdigest()


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
        # Print out all authorization headers for debugging
        print("All request headers:", request.META)
        
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        print("Authorization Header:", auth_header)
        
        if not auth_header.startswith('Bearer '):
            print("No Bearer token found")
            return None
            
        token = auth_header.split(' ')[1]
        if not token:
            print("Token is empty")
            return None
            
        payload = JWTHandler.decode_token(token)
        print("Decoded Payload:", payload)
        
        if payload is None:
            print("Invalid or expired token")
            raise exceptions.AuthenticationFailed('Invalid token or token expired')
            
        user_id = payload.get('user_id')
        print("User ID from token:", user_id)
        
        user_dict = UserModel.get_user_by_id(user_id)
        print("User Dictionary:", user_dict)
        
        if not user_dict:
            print("User not found")
            raise exceptions.AuthenticationFailed('User not found')
            
        if not user_dict.get('is_approved', False):
            print("User not approved")
            raise exceptions.AuthenticationFailed('User not approved')
            
        # Convert the dictionary to a User object
        user = User(**user_dict)
            
        return (user, token)
        
    def authenticate_header(self, request):
        return 'Bearer'