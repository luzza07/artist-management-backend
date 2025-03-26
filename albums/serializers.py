from rest_framework import serializers

class AlbumSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    artist_id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    release_year = serializers.DateField()
    photo_url = serializers.CharField(max_length=255, required=False, allow_null=True)