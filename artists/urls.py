from django.urls import path
from .views import *

urlpatterns = [
    path('profile/', ArtistProfileView.as_view(), name='artist-profile'),
    path('albums/', AlbumView.as_view(), name='artist-albums'),
    path('tracks/', MusicView.as_view(), name='artist-tracks'),
    path("export-artists/", ExportArtistsCSVView.as_view(), name="export_artists_csv"),
    path("import-artists/", ImportArtistsCSVView.as_view(), name="import_artists_csv"),
    path('music/<int:artist_id>/', ArtistMusicView.as_view(), name='artist-songs'),
]