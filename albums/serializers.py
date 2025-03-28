from rest_framework import serializers
from datetime import datetime

class AlbumSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    artist_id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    release_year = serializers.DateField()
    genre = serializers.ChoiceField(choices=["rnb", "country", "classic", "rock", "jazz","mix"])  
    photo_url = serializers.CharField(max_length=255, required=False, allow_null=True)
    tracklist = serializers.ListField(child=serializers.CharField(max_length=255), required=False, allow_null=True)
    total_tracks = serializers.IntegerField(required=False, allow_null=True)
    total_duration = serializers.CharField(max_length=255, required=False, allow_null=True)  # Or use serializers.DurationField() if handling time durations
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    def validate_release_year(self, value):
        """ Ensure release_year is in the correct format (YYYY-MM-DD). """
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                raise serializers.ValidationError("Invalid date format. Use YYYY-MM-DD.")
        return value 

    def validate(self, data):
        """
        Custom validation to ensure that the total_tracks matches the length of the tracklist
        """
        if data.get('total_tracks') is not None and data.get('tracklist') is not None:
            if len(data['tracklist']) != data['total_tracks']:
                raise serializers.ValidationError("Total tracks do not match the number of tracks in the tracklist.")
        return data
