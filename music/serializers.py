from rest_framework import serializers

class MusicSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    album_id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    genre = serializers.ChoiceField(choices=['rnb', 'country', 'classic', 'rock', 'jazz'])