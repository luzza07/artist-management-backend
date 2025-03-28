from rest_framework import serializers

class MusicSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    album_id = serializers.IntegerField()
    music_id = serializers.CharField(max_length=255, read_only=True)
    title = serializers.CharField(max_length=255)
    genre = serializers.ChoiceField(choices=['rnb', 'country', 'classic', 'rock', 'jazz', 'mix'])
    duration = serializers.DurationField(required=True)  # Duration as an interval
    release_date = serializers.DateField(required=True)  # Release date of the track
    cover_page = serializers.CharField(max_length=255, required=False, allow_null=True)  # URL or file path to cover image
    track_number = serializers.IntegerField(read_only=True)  # Track number in the album

    def validate_genre(self, value):
        """ Validate that genre is one of the defined options. """
        valid_genres = ['rnb', 'country', 'classic', 'rock', 'jazz', 'mix']
        if value not in valid_genres:
            raise serializers.ValidationError(f"Genre must be one of: {', '.join(valid_genres)}")
        return value
