from rest_framework import serializers
from .models import UserModel

class UserSignupSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    phone = serializers.CharField(max_length=15, required=False)
    dob = serializers.DateField(required=False)
    gender = serializers.ChoiceField(choices=['m', 'f', 'o'])
    address = serializers.CharField(max_length=255, required=False)
    role_type = serializers.ChoiceField(choices=['super_admin', 'artist_manager', 'artist'])
    
    def validate(self, data):
        # Check if passwords match
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords don't match"})
            
        # Check if email already exists
        user = UserModel.get_user_by_email(data['email'])
        if user:
            raise serializers.ValidationError({"email": "User with this email already exists"})
            
        return data

    def create(self, validated_data):
        """
        Creates a new user using raw SQL.
        """
        # Remove confirm_password from the data
        validated_data.pop('confirm_password')
        
        # Create the user
        user_id = UserModel.create_user(**validated_data)
        
        # If the role is super_admin or artist_manager, create an approval request
        if validated_data['role_type'] in ['super_admin', 'artist_manager']:
            requested_by_id = self.context['request'].user.id  # Assuming the request is made by an authenticated user
            UserModel.create_approval_request(user_id, requested_by_id)
        
        return {"user_id": user_id}


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class UserApprovalSerializer(serializers.Serializer):
    approver_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    def validate(self, data):
        # Check if the approver is a super_admin
        approver = UserModel.get_user_by_id(data['approver_id'])
        if not approver or approver['role_type'] != 'super_admin':
            raise serializers.ValidationError({"approver_id": "Only super_admin can approve users"})
        
        # Check if the user exists and is pending approval
        user = UserModel.get_user_by_id(data['user_id'])
        if not user or user['is_approved']:
            raise serializers.ValidationError({"user_id": "User not found or already approved"})
        
        return data

    def create(self, validated_data):
        """
        Approves a user and their approval request.
        """
        user_id = validated_data['user_id']
        approver_id = validated_data['approver_id']
        
        # Approve the user
        UserModel.approve_user(user_id)
        
        return {"user_id": user_id, "approved_by": approver_id}


class PendingUsersSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    role_type = serializers.CharField()
    created_at = serializers.DateTimeField()