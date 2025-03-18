from rest_framework import serializers

class UserSignupSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    phone = serializers.CharField(max_length=20, required=False)
    dob = serializers.DateTimeField(required=False)
    gender = serializers.ChoiceField(choices=["m", "f", "o"])
    address = serializers.CharField(max_length=255, required=False)
    role_type = serializers.ChoiceField(choices=["super_admin", "artist_manager", "artist"])

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
